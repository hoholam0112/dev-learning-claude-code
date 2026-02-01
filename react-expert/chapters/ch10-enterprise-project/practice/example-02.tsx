/**
 * 챕터 10 - 예제 02: 실시간 대시보드 + 데이터 시각화
 *
 * 이 예제는 다음을 다룹니다:
 *   1. WebSocket 기반 실시간 데이터 업데이트
 *   2. KPI 카드 (핵심 지표 표시)
 *   3. 차트 컴포넌트 (Recharts 활용)
 *   4. 데이터 테이블 (정렬, 필터, 페이지네이션)
 *
 * 실행 방법:
 *   1. 의존성 설치:
 *      cd admin-dashboard
 *      npm install recharts date-fns
 *
 *   2. 이 파일을 참고하여 구현 후:
 *      npm run dev
 */

import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
  type ReactNode,
} from 'react';

// ============================================================
// 1. 타입 정의
// ============================================================

/** 대시보드 메트릭 */
interface DashboardMetrics {
  activeUsers: number;
  totalRevenue: number;
  newOrders: number;
  conversionRate: number;
  serverUptime: number;
  errorRate: number;
}

/** 차트 데이터 포인트 */
interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

/** 시계열 데이터 */
interface TimeSeriesData {
  revenue: ChartDataPoint[];
  users: ChartDataPoint[];
  orders: ChartDataPoint[];
}

/** 실시간 이벤트 */
interface RealtimeEvent {
  type: 'metrics_update' | 'new_order' | 'user_activity' | 'alert';
  data: unknown;
  timestamp: string;
}

/** 활동 로그 */
interface ActivityLog {
  id: string;
  user: string;
  action: string;
  target: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error';
}

// ============================================================
// 2. WebSocket 훅
// ============================================================

interface WebSocketOptions {
  /** 자동 재연결 */
  reconnect?: boolean;
  /** 재연결 간격 (ms) */
  reconnectInterval?: number;
  /** 최대 재연결 시도 횟수 */
  maxReconnectAttempts?: number;
  /** 연결 시 콜백 */
  onOpen?: () => void;
  /** 메시지 수신 콜백 */
  onMessage?: (event: RealtimeEvent) => void;
  /** 에러 콜백 */
  onError?: (error: Event) => void;
  /** 연결 종료 콜백 */
  onClose?: () => void;
}

interface WebSocketReturn {
  /** 연결 상태 */
  isConnected: boolean;
  /** 마지막 수신 메시지 */
  lastMessage: RealtimeEvent | null;
  /** 메시지 전송 */
  sendMessage: (data: unknown) => void;
  /** 수동 연결 */
  connect: () => void;
  /** 수동 연결 종료 */
  disconnect: () => void;
  /** 재연결 시도 횟수 */
  reconnectCount: number;
}

/**
 * useWebSocket 훅
 *
 * WebSocket 연결을 관리하며 다음 기능을 제공합니다:
 * - 자동 재연결 (지수 백오프)
 * - 하트비트 (ping/pong)
 * - 메시지 타입별 구독
 * - 언마운트 시 자동 정리
 */
export function useWebSocket(
  url: string,
  options: WebSocketOptions = {}
): WebSocketReturn {
  const {
    reconnect = true,
    reconnectInterval = 1000,
    maxReconnectAttempts = 10,
    onOpen,
    onMessage,
    onError,
    onClose,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<RealtimeEvent | null>(null);
  const [reconnectCount, setReconnectCount] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval>>();
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        setIsConnected(true);
        setReconnectCount(0);
        onOpen?.();

        // 하트비트 시작 (30초마다)
        heartbeatTimerRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const data: RealtimeEvent = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch {
          console.error('[WebSocket] 메시지 파싱 실패:', event.data);
        }
      };

      ws.onerror = (error) => {
        if (!mountedRef.current) return;
        onError?.(error);
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setIsConnected(false);
        onClose?.();

        // 하트비트 정지
        if (heartbeatTimerRef.current) {
          clearInterval(heartbeatTimerRef.current);
        }

        // 자동 재연결 (지수 백오프)
        if (reconnect && reconnectCount < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(2, reconnectCount);
          console.log(
            `[WebSocket] ${delay}ms 후 재연결 시도... (${reconnectCount + 1}/${maxReconnectAttempts})`
          );
          reconnectTimerRef.current = setTimeout(() => {
            setReconnectCount((prev) => prev + 1);
            connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('[WebSocket] 연결 실패:', error);
    }
  }, [url, reconnect, reconnectInterval, maxReconnectAttempts, reconnectCount, onOpen, onMessage, onError, onClose]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('[WebSocket] 연결되지 않은 상태에서 메시지 전송 시도');
    }
  }, []);

  // 자동 연결/정리
  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [url]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    reconnectCount,
  };
}

// ============================================================
// 3. KPI 카드 컴포넌트
// ============================================================

interface KPICardProps {
  /** 지표 제목 */
  title: string;
  /** 현재 값 */
  value: number | string;
  /** 이전 기간 대비 변화율 (%) */
  trend?: number;
  /** 아이콘 */
  icon?: string;
  /** 값 포맷 함수 */
  formatValue?: (value: number | string) => string;
  /** 로딩 상태 */
  isLoading?: boolean;
  /** 실시간 업데이트 표시 */
  isLive?: boolean;
}

export function KPICard({
  title,
  value,
  trend,
  icon,
  formatValue,
  isLoading = false,
  isLive = false,
}: KPICardProps) {
  const displayValue = formatValue ? formatValue(value) : String(value);
  const trendColor = trend && trend > 0 ? '#4CAF50' : trend && trend < 0 ? '#f44336' : '#9E9E9E';
  const trendIcon = trend && trend > 0 ? '↑' : trend && trend < 0 ? '↓' : '→';

  if (isLoading) {
    return (
      <div
        role="status"
        aria-label={`${title} 로딩 중`}
        style={{
          padding: '20px',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        }}
      >
        <div className="skeleton-line" style={{ width: '60%', height: '14px' }} />
        <div className="skeleton-line" style={{ width: '40%', height: '28px', marginTop: '8px' }} />
      </div>
    );
  }

  return (
    <article
      aria-label={`${title}: ${displayValue}`}
      style={{
        padding: '20px',
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        position: 'relative',
      }}
    >
      {/* 실시간 표시 */}
      {isLive && (
        <span
          aria-label="실시간 업데이트"
          style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: '#4CAF50',
            animation: 'pulse 2s infinite',
          }}
        />
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>{title}</p>
          <p style={{ margin: '8px 0 0', fontSize: '28px', fontWeight: 'bold' }}>
            {displayValue}
          </p>
        </div>
        {icon && <span style={{ fontSize: '32px' }}>{icon}</span>}
      </div>

      {trend !== undefined && (
        <div
          style={{ marginTop: '12px', fontSize: '13px', color: trendColor }}
          aria-label={`전 기간 대비 ${Math.abs(trend)}% ${trend > 0 ? '증가' : '감소'}`}
        >
          <span>{trendIcon}</span>
          <span style={{ marginLeft: '4px' }}>{Math.abs(trend).toFixed(1)}%</span>
          <span style={{ color: '#999', marginLeft: '4px' }}>전 기간 대비</span>
        </div>
      )}
    </article>
  );
}

// ============================================================
// 4. 차트 래퍼 컴포넌트 (Recharts 활용)
// ============================================================

/**
 * 차트 컴포넌트는 Recharts를 사용합니다.
 * 아래는 Recharts 컴포넌트의 사용 패턴을 보여주는 의사 코드입니다.
 *
 * 실제 구현 시 다음과 같이 import합니다:
 * import {
 *   LineChart, Line, BarChart, Bar,
 *   XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
 * } from 'recharts';
 */

interface ChartCardProps {
  title: string;
  data: ChartDataPoint[];
  type: 'line' | 'bar' | 'area';
  color?: string;
  height?: number;
  isLoading?: boolean;
}

export function ChartCard({
  title,
  data,
  type,
  color = '#2196F3',
  height = 300,
  isLoading = false,
}: ChartCardProps) {
  if (isLoading) {
    return (
      <div
        role="status"
        aria-label={`${title} 차트 로딩 중`}
        style={{
          padding: '20px',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
          height: `${height + 60}px`,
        }}
      >
        <div className="skeleton-line" style={{ width: '40%', height: '20px' }} />
        <div className="skeleton-chart" style={{ height: `${height}px`, marginTop: '16px' }} />
      </div>
    );
  }

  return (
    <article
      aria-label={`${title} 차트`}
      style={{
        padding: '20px',
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      }}
    >
      <h3 style={{ margin: '0 0 16px', fontSize: '16px' }}>{title}</h3>

      {/*
        Recharts 사용 예시:

        <ResponsiveContainer width="100%" height={height}>
          {type === 'line' ? (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      */}

      {/* 데모용 간단 차트 (SVG) */}
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 ${data.length * 60} ${height}`}
        role="img"
        aria-label={`${title} - ${data.length}개 데이터 포인트`}
      >
        {type === 'bar'
          ? data.map((point, i) => {
              const maxValue = Math.max(...data.map((d) => d.value));
              const barHeight = (point.value / maxValue) * (height - 40);
              return (
                <g key={i}>
                  <rect
                    x={i * 60 + 10}
                    y={height - barHeight - 20}
                    width={40}
                    height={barHeight}
                    fill={color}
                    rx={4}
                    opacity={0.8}
                  />
                  <text
                    x={i * 60 + 30}
                    y={height - 4}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#666"
                  >
                    {point.date}
                  </text>
                </g>
              );
            })
          : (() => {
              const maxValue = Math.max(...data.map((d) => d.value));
              const points = data
                .map((point, i) => {
                  const x = i * 60 + 30;
                  const y = height - (point.value / maxValue) * (height - 40) - 20;
                  return `${x},${y}`;
                })
                .join(' ');
              return (
                <polyline
                  points={points}
                  fill="none"
                  stroke={color}
                  strokeWidth={2}
                />
              );
            })()}
      </svg>
    </article>
  );
}

// ============================================================
// 5. 활동 로그 테이블
// ============================================================

interface ActivityTableProps {
  activities: ActivityLog[];
  isLoading?: boolean;
}

export function ActivityTable({ activities, isLoading }: ActivityTableProps) {
  const [sortField, setSortField] = useState<keyof ActivityLog>('timestamp');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const sortedActivities = useMemo(() => {
    return [...activities].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      const comparison = String(aVal).localeCompare(String(bVal));
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [activities, sortField, sortDirection]);

  const handleSort = (field: keyof ActivityLog) => {
    if (sortField === field) {
      setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const statusStyles: Record<string, { background: string; color: string }> = {
    success: { background: '#e8f5e9', color: '#2e7d32' },
    warning: { background: '#fff3e0', color: '#e65100' },
    error: { background: '#ffebee', color: '#c62828' },
  };

  const statusLabels: Record<string, string> = {
    success: '성공',
    warning: '경고',
    error: '오류',
  };

  if (isLoading) {
    return (
      <div role="status" aria-label="활동 로그 로딩 중">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="skeleton-row" style={{ height: '40px', marginBottom: '4px' }} />
        ))}
      </div>
    );
  }

  return (
    <div
      style={{
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        overflow: 'hidden',
      }}
    >
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #eee' }}>
        <h3 style={{ margin: 0 }}>최근 활동</h3>
      </div>

      <table
        role="table"
        aria-label="활동 로그"
        style={{ width: '100%', borderCollapse: 'collapse' }}
      >
        <thead>
          <tr>
            {[
              { key: 'user' as const, label: '사용자' },
              { key: 'action' as const, label: '작업' },
              { key: 'target' as const, label: '대상' },
              { key: 'status' as const, label: '상태' },
              { key: 'timestamp' as const, label: '시간' },
            ].map(({ key, label }) => (
              <th
                key={key}
                onClick={() => handleSort(key)}
                style={{
                  padding: '12px 16px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  borderBottom: '2px solid #eee',
                  userSelect: 'none',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#666',
                }}
                aria-sort={
                  sortField === key
                    ? sortDirection === 'asc'
                      ? 'ascending'
                      : 'descending'
                    : 'none'
                }
              >
                {label}
                {sortField === key && (sortDirection === 'asc' ? ' ↑' : ' ↓')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedActivities.map((activity) => (
            <tr key={activity.id}>
              <td style={{ padding: '10px 16px', borderBottom: '1px solid #f5f5f5' }}>
                {activity.user}
              </td>
              <td style={{ padding: '10px 16px', borderBottom: '1px solid #f5f5f5' }}>
                {activity.action}
              </td>
              <td style={{ padding: '10px 16px', borderBottom: '1px solid #f5f5f5' }}>
                {activity.target}
              </td>
              <td style={{ padding: '10px 16px', borderBottom: '1px solid #f5f5f5' }}>
                <span
                  style={{
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    ...statusStyles[activity.status],
                  }}
                >
                  {statusLabels[activity.status]}
                </span>
              </td>
              <td style={{ padding: '10px 16px', borderBottom: '1px solid #f5f5f5', fontSize: '13px', color: '#666' }}>
                {new Date(activity.timestamp).toLocaleString('ko-KR')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================================
// 6. 대시보드 페이지 (종합)
// ============================================================

// 모킹 데이터
const mockMetrics: DashboardMetrics = {
  activeUsers: 1247,
  totalRevenue: 45200000,
  newOrders: 89,
  conversionRate: 3.2,
  serverUptime: 99.97,
  errorRate: 0.12,
};

const mockChartData: ChartDataPoint[] = [
  { date: '1월', value: 3200 },
  { date: '2월', value: 4100 },
  { date: '3월', value: 3800 },
  { date: '4월', value: 5200 },
  { date: '5월', value: 4900 },
  { date: '6월', value: 6100 },
];

const mockActivities: ActivityLog[] = [
  { id: '1', user: '김관리자', action: '사용자 생성', target: 'user@example.com', timestamp: '2024-01-15T09:30:00Z', status: 'success' },
  { id: '2', user: '이편집자', action: '게시글 수정', target: 'React 가이드', timestamp: '2024-01-15T09:25:00Z', status: 'success' },
  { id: '3', user: '시스템', action: 'API 에러', target: '/api/payments', timestamp: '2024-01-15T09:20:00Z', status: 'error' },
  { id: '4', user: '박사용자', action: '로그인 실패', target: 'park@example.com', timestamp: '2024-01-15T09:15:00Z', status: 'warning' },
  { id: '5', user: '김관리자', action: '설정 변경', target: '알림 설정', timestamp: '2024-01-15T09:10:00Z', status: 'success' },
];

export function RealTimeDashboard() {
  const [metrics, setMetrics] = useState(mockMetrics);
  const [isLive, setIsLive] = useState(false);

  // 실시간 데이터 시뮬레이션 (실제로는 useWebSocket 사용)
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        activeUsers: prev.activeUsers + Math.floor(Math.random() * 10 - 5),
        newOrders: prev.newOrders + Math.floor(Math.random() * 3),
        errorRate: Math.max(0, prev.errorRate + (Math.random() - 0.5) * 0.1),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, [isLive]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0 }}>대시보드 개요</h2>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            checked={isLive}
            onChange={(e) => setIsLive(e.target.checked)}
          />
          실시간 업데이트
          {isLive && (
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#4CAF50', display: 'inline-block' }} />
          )}
        </label>
      </div>

      {/* KPI 카드 그리드 */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        <KPICard
          title="활성 사용자"
          value={metrics.activeUsers}
          trend={12.5}
          icon="👥"
          formatValue={(v) => `${Number(v).toLocaleString()}명`}
          isLive={isLive}
        />
        <KPICard
          title="총 매출"
          value={metrics.totalRevenue}
          trend={8.3}
          icon="💰"
          formatValue={(v) => `${(Number(v) / 10000).toLocaleString()}만원`}
          isLive={isLive}
        />
        <KPICard
          title="신규 주문"
          value={metrics.newOrders}
          trend={-2.1}
          icon="📦"
          formatValue={(v) => `${v}건`}
          isLive={isLive}
        />
        <KPICard
          title="전환율"
          value={metrics.conversionRate}
          trend={0.5}
          icon="📈"
          formatValue={(v) => `${Number(v).toFixed(1)}%`}
        />
        <KPICard
          title="서버 가동률"
          value={metrics.serverUptime}
          icon="🖥️"
          formatValue={(v) => `${Number(v).toFixed(2)}%`}
        />
        <KPICard
          title="에러율"
          value={metrics.errorRate}
          trend={-15.2}
          icon="⚠️"
          formatValue={(v) => `${Number(v).toFixed(2)}%`}
          isLive={isLive}
        />
      </div>

      {/* 차트 그리드 */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        <ChartCard
          title="월별 매출 추이"
          data={mockChartData}
          type="line"
          color="#2196F3"
        />
        <ChartCard
          title="월별 주문 수"
          data={mockChartData.map((d) => ({ ...d, value: Math.floor(d.value / 50) }))}
          type="bar"
          color="#4CAF50"
        />
      </div>

      {/* 활동 로그 테이블 */}
      <ActivityTable activities={mockActivities} />
    </div>
  );
}

export default RealTimeDashboard;
