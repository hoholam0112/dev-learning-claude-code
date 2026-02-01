/**
 * 챕터 05 - 예제 2: 타입 안전한 폼 라이브러리
 *
 * TypeScript의 고급 타입 기능을 활용하여
 * 완전한 타입 안전성을 제공하는 폼 라이브러리를 구현합니다.
 *
 * 핵심 목표:
 * - 스키마에서 필드 이름, 값 타입을 자동 추론
 * - 중첩 객체 경로를 dot notation으로 접근
 * - 유효성 검사 함수의 매개변수 타입 자동 추론
 * - 제출 시 전체 폼 데이터의 타입 보장
 *
 * 실행 방법:
 *   npx tsx practice/example-02.tsx
 */

// ============================================================
// 1. 핵심 타입 정의
// ============================================================

/**
 * 경로 타입: 중첩 객체의 dot notation 경로를 문자열 유니온으로 생성
 *
 * 예: Path<{ name: string; address: { city: string; zip: string } }>
 *     = 'name' | 'address' | 'address.city' | 'address.zip'
 */
type Path<T, Prefix extends string = ""> = T extends object
  ? {
      [K in keyof T & string]:
        | `${Prefix}${K}`
        | Path<T[K], `${Prefix}${K}.`>;
    }[keyof T & string]
  : never;

/**
 * PathValue: 특정 경로에 해당하는 값의 타입을 추출
 *
 * 예: PathValue<{ address: { city: string } }, 'address.city'>
 *     = string
 */
type PathValue<T, P extends string> = P extends `${infer K}.${infer Rest}`
  ? K extends keyof T
    ? PathValue<T[K], Rest>
    : never
  : P extends keyof T
    ? T[P]
    : never;

/**
 * 리프 경로: 원시값(비객체)에 해당하는 경로만 추출
 *
 * 예: LeafPath<{ name: string; address: { city: string } }>
 *     = 'name' | 'address.city'  (address는 제외)
 */
type LeafPath<T, Prefix extends string = ""> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? LeafPath<T[K], `${Prefix}${K}.`>
        : `${Prefix}${K}`;
    }[keyof T & string]
  : never;

// ============================================================
// 2. 폼 상태 타입
// ============================================================

/** 필드 에러 타입 */
type FieldErrors<T> = Partial<Record<LeafPath<T>, string>>;

/** 필드 터치 상태 */
type FieldTouched<T> = Partial<Record<LeafPath<T>, boolean>>;

/** 필드 더티 상태 */
type FieldDirty<T> = Partial<Record<LeafPath<T>, boolean>>;

/** 유효성 검사 함수 맵 */
type ValidationRules<T> = Partial<{
  [P in LeafPath<T>]: (value: PathValue<T, P>) => string | null;
}>;

/** 폼 전체 상태 */
interface FormState<T> {
  values: T;
  errors: FieldErrors<T>;
  touched: FieldTouched<T>;
  dirty: FieldDirty<T>;
  isValid: boolean;
  isSubmitting: boolean;
  submitCount: number;
}

/** 폼 설정 */
interface FormConfig<T> {
  defaultValues: T;
  validate?: ValidationRules<T>;
  onSubmit?: (values: T) => void | Promise<void>;
}

// ============================================================
// 3. 유틸리티 함수
// ============================================================

/**
 * 경로로 중첩 객체의 값을 읽기
 */
function getByPath<T extends Record<string, any>>(
  obj: T,
  path: string
): any {
  return path.split(".").reduce((current, key) => current?.[key], obj);
}

/**
 * 경로로 중첩 객체의 값을 설정 (불변 업데이트)
 */
function setByPath<T extends Record<string, any>>(
  obj: T,
  path: string,
  value: any
): T {
  const keys = path.split(".");

  if (keys.length === 1) {
    return { ...obj, [keys[0]]: value };
  }

  const [first, ...rest] = keys;
  return {
    ...obj,
    [first]: setByPath(
      (obj[first] as Record<string, any>) ?? {},
      rest.join("."),
      value
    ),
  };
}

// ============================================================
// 4. 타입 안전한 폼 엔진
// ============================================================

/**
 * createForm - 타입 안전한 폼 인스턴스를 생성합니다.
 *
 * 핵심: 모든 메서드의 매개변수 타입이 스키마 T에서 자동 추론됩니다.
 * - register('name') → string 타입의 입력
 * - register('age') → number 타입의 입력
 * - register('address.city') → string 타입의 입력
 */
class TypedForm<T extends Record<string, any>> {
  private state: FormState<T>;
  private config: FormConfig<T>;
  private listeners = new Set<() => void>();

  constructor(config: FormConfig<T>) {
    this.config = config;
    this.state = {
      values: { ...config.defaultValues },
      errors: {} as FieldErrors<T>,
      touched: {} as FieldTouched<T>,
      dirty: {} as FieldDirty<T>,
      isValid: true,
      isSubmitting: false,
      submitCount: 0,
    };
  }

  /** 현재 상태 조회 */
  getState(): FormState<T> {
    return { ...this.state };
  }

  /** 필드 값 조회 */
  getValue<P extends LeafPath<T>>(path: P): PathValue<T, P> {
    return getByPath(this.state.values, path);
  }

  /** 필드 값 설정 */
  setValue<P extends LeafPath<T>>(
    path: P,
    value: PathValue<T, P>
  ): void {
    this.state = {
      ...this.state,
      values: setByPath(this.state.values, path, value),
      dirty: { ...this.state.dirty, [path]: true } as FieldDirty<T>,
    };

    // 유효성 검사 실행
    if (this.config.validate) {
      const validator = (this.config.validate as any)[path];
      if (validator) {
        const error = validator(value);
        this.state.errors = {
          ...this.state.errors,
          [path]: error,
        } as FieldErrors<T>;
      }
    }

    this.updateValidity();
    this.notifyListeners();
  }

  /** 필드 터치 */
  setTouched<P extends LeafPath<T>>(path: P): void {
    this.state = {
      ...this.state,
      touched: { ...this.state.touched, [path]: true } as FieldTouched<T>,
    };

    // 터치 시 유효성 검사
    if (this.config.validate) {
      const validator = (this.config.validate as any)[path];
      if (validator) {
        const value = this.getValue(path);
        const error = validator(value);
        this.state.errors = {
          ...this.state.errors,
          [path]: error,
        } as FieldErrors<T>;
      }
    }

    this.notifyListeners();
  }

  /** 필드 에러 조회 */
  getError<P extends LeafPath<T>>(path: P): string | null {
    return (this.state.errors as any)[path] ?? null;
  }

  /** 필드가 터치되었는지 확인 */
  isTouched<P extends LeafPath<T>>(path: P): boolean {
    return (this.state.touched as any)[path] ?? false;
  }

  /** 에러를 표시해야 하는지 (터치됨 + 에러 있음) */
  shouldShowError<P extends LeafPath<T>>(path: P): boolean {
    return this.isTouched(path) && this.getError(path) !== null;
  }

  /**
   * register - 필드를 폼에 등록합니다.
   *
   * 반환값은 input 요소에 스프레드할 수 있는 props 객체입니다.
   * 타입 안전: path에 해당하는 값의 타입으로 value가 제한됩니다.
   */
  register<P extends LeafPath<T>>(path: P) {
    return {
      name: path,
      value: this.getValue(path),
      onChange: (value: PathValue<T, P>) => this.setValue(path, value),
      onBlur: () => this.setTouched(path),
      error: this.getError(path),
      touched: this.isTouched(path),
    };
  }

  /** 전체 유효성 검사 */
  validateAll(): boolean {
    if (!this.config.validate) return true;

    let isValid = true;
    const errors = {} as FieldErrors<T>;

    for (const [path, validator] of Object.entries(this.config.validate)) {
      if (typeof validator === "function") {
        const value = getByPath(this.state.values, path);
        const error = (validator as (v: any) => string | null)(value);
        if (error) {
          (errors as any)[path] = error;
          isValid = false;
        }
      }
    }

    this.state = { ...this.state, errors, isValid };
    this.notifyListeners();
    return isValid;
  }

  /** 폼 제출 */
  async handleSubmit(): Promise<boolean> {
    this.state.submitCount += 1;

    // 모든 필드 터치 처리
    if (this.config.validate) {
      for (const path of Object.keys(this.config.validate)) {
        (this.state.touched as any)[path] = true;
      }
    }

    // 전체 유효성 검사
    const isValid = this.validateAll();
    if (!isValid) return false;

    // 제출 실행
    if (this.config.onSubmit) {
      this.state.isSubmitting = true;
      this.notifyListeners();

      try {
        await this.config.onSubmit(this.state.values);
        return true;
      } catch (error) {
        console.error("폼 제출 실패:", error);
        return false;
      } finally {
        this.state.isSubmitting = false;
        this.notifyListeners();
      }
    }

    return true;
  }

  /** 폼 초기화 */
  reset(): void {
    this.state = {
      values: { ...this.config.defaultValues },
      errors: {} as FieldErrors<T>,
      touched: {} as FieldTouched<T>,
      dirty: {} as FieldDirty<T>,
      isValid: true,
      isSubmitting: false,
      submitCount: 0,
    };
    this.notifyListeners();
  }

  /** 구독 */
  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private updateValidity(): void {
    this.state.isValid = Object.values(this.state.errors).every(
      (error) => error === null || error === undefined
    );
  }

  private notifyListeners(): void {
    this.listeners.forEach((l) => l());
  }
}

// ============================================================
// 5. 데모 실행
// ============================================================

console.log("╔══════════════════════════════════════════════════════════╗");
console.log("║ 타입 안전한 폼 라이브러리 데모                           ║");
console.log("╚══════════════════════════════════════════════════════════╝\n");

// --- 폼 스키마 정의 ---
interface UserRegistrationForm {
  name: string;
  email: string;
  age: number;
  password: string;
  address: {
    city: string;
    zipCode: string;
    detail: string;
  };
  preferences: {
    newsletter: boolean;
    theme: "light" | "dark";
  };
}

// --- Path 타입 데모 ---
console.log("=== 1. Path 타입 추론 ===\n");

// 이 타입들은 컴파일 타임에 자동 생성됩니다
type UserPaths = LeafPath<UserRegistrationForm>;
// = 'name' | 'email' | 'age' | 'password'
//   | 'address.city' | 'address.zipCode' | 'address.detail'
//   | 'preferences.newsletter' | 'preferences.theme'

console.log("LeafPath<UserRegistrationForm>:");
console.log("  'name' | 'email' | 'age' | 'password'");
console.log("  | 'address.city' | 'address.zipCode' | 'address.detail'");
console.log("  | 'preferences.newsletter' | 'preferences.theme'\n");

// PathValue 추론
console.log("PathValue<UserRegistrationForm, 'name'> = string");
console.log("PathValue<UserRegistrationForm, 'age'> = number");
console.log("PathValue<UserRegistrationForm, 'address.city'> = string");
console.log("PathValue<UserRegistrationForm, 'preferences.theme'> = 'light' | 'dark'");

// --- 폼 인스턴스 생성 ---
console.log("\n\n=== 2. 폼 인스턴스 생성 ===\n");

const form = new TypedForm<UserRegistrationForm>({
  defaultValues: {
    name: "",
    email: "",
    age: 0,
    password: "",
    address: {
      city: "",
      zipCode: "",
      detail: "",
    },
    preferences: {
      newsletter: true,
      theme: "light",
    },
  },
  validate: {
    name: (v) => (v.length >= 2 ? null : "이름은 2글자 이상이어야 합니다"),
    email: (v) => (v.includes("@") ? null : "유효한 이메일을 입력하세요"),
    age: (v) => (v >= 0 && v <= 150 ? null : "나이는 0~150 사이여야 합니다"),
    password: (v) => (v.length >= 8 ? null : "비밀번호는 8자 이상이어야 합니다"),
    "address.city": (v) => (v.length > 0 ? null : "도시를 입력하세요"),
    "address.zipCode": (v) =>
      /^\d{5}$/.test(v) ? null : "우편번호는 5자리 숫자입니다",
  },
  onSubmit: async (values) => {
    console.log("  폼 제출 성공:", JSON.stringify(values, null, 2));
  },
});

console.log("폼이 생성되었습니다.");
console.log("초기값:", JSON.stringify(form.getState().values, null, 2));

// --- register 패턴 ---
console.log("\n\n=== 3. register 패턴 ===\n");

const nameField = form.register("name");
console.log("register('name'):");
console.log(`  name: "${nameField.name}"`);
console.log(`  value: "${nameField.value}" (타입: string)`);
console.log(`  error: ${nameField.error}`);
console.log(`  touched: ${nameField.touched}`);

const cityField = form.register("address.city");
console.log("\nregister('address.city'):");
console.log(`  name: "${cityField.name}"`);
console.log(`  value: "${cityField.value}" (타입: string)`);

// --- 값 설정 및 유효성 검사 ---
console.log("\n\n=== 4. 값 설정 및 유효성 검사 ===\n");

form.setValue("name", "김");
form.setTouched("name");
console.log("setValue('name', '김') + setTouched:");
console.log(`  값: "${form.getValue("name")}"`);
console.log(`  에러: ${form.getError("name")}`);
console.log(`  표시 여부: ${form.shouldShowError("name")}`);

form.setValue("name", "김개발");
console.log("\nsetValue('name', '김개발'):");
console.log(`  값: "${form.getValue("name")}"`);
console.log(`  에러: ${form.getError("name")}`);

form.setValue("email", "invalid-email");
form.setTouched("email");
console.log("\nsetValue('email', 'invalid-email'):");
console.log(`  에러: ${form.getError("email")}`);

form.setValue("email", "kim@dev.com");
console.log("\nsetValue('email', 'kim@dev.com'):");
console.log(`  에러: ${form.getError("email")}`);

// 중첩 경로 설정
form.setValue("address.city", "서울");
form.setValue("address.zipCode", "12345");
console.log("\nsetValue('address.city', '서울'):");
console.log(`  address.city: "${form.getValue("address.city")}"`);
console.log(`  address.zipCode: "${form.getValue("address.zipCode")}"`);

// --- 폼 제출 ---
console.log("\n\n=== 5. 폼 제출 ===\n");

// 불완전한 상태에서 제출 시도
form.setValue("age", 25);
form.setValue("password", "12345"); // 8자 미만
console.log("비밀번호가 짧은 상태에서 제출 시도...");

form.handleSubmit().then((success) => {
  console.log(`  제출 결과: ${success ? "성공" : "실패"}`);

  if (!success) {
    console.log("  에러 목록:");
    const state = form.getState();
    Object.entries(state.errors).forEach(([field, error]) => {
      if (error) console.log(`    ${field}: ${error}`);
    });
  }

  // 비밀번호 수정 후 재제출
  form.setValue("password", "securePassword123");
  form.setValue("address.detail", "강남구 테헤란로");

  console.log("\n비밀번호 수정 후 재제출...");
  return form.handleSubmit();
}).then((success) => {
  console.log(`  제출 결과: ${success ? "성공" : "실패"}`);

  // --- 타입 안전성 요약 ---
  console.log("\n\n=== 6. 타입 안전성 요약 ===\n");
  console.log(`
타입 안전성이 보장되는 곳:
  1. register('필드명')
     - 자동 완성으로 유효한 필드명만 입력 가능
     - 'name', 'email', 'address.city' 등
     - 존재하지 않는 'foo.bar' 입력 시 컴파일 에러

  2. setValue(path, value)
     - path에 따라 value의 타입이 자동 결정
     - setValue('name', 123) → 컴파일 에러 (string 필요)
     - setValue('age', 'abc') → 컴파일 에러 (number 필요)

  3. validate 함수
     - 각 필드의 검증 함수 매개변수가 해당 필드 타입
     - validate.name: (v: string) => ...
     - validate.age: (v: number) => ...

  4. onSubmit(values)
     - values가 완전한 UserRegistrationForm 타입
     - 모든 필드가 올바른 타입으로 보장됨

  5. getByPath / setByPath
     - 중첩 객체를 안전하게 읽기/쓰기
     - 경로가 타입 레벨에서 검증됨
  `);

  console.log("✅ 타입 안전한 폼 라이브러리 데모 완료!");
});

export {
  TypedForm,
  Path,
  PathValue,
  LeafPath,
  FieldErrors,
  FormState,
  FormConfig,
  ValidationRules,
  getByPath,
  setByPath,
};
