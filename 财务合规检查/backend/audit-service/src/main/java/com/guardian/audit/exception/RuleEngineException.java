package com.guardian.audit.exception;

/**
 * 规则引擎异常类
 * 用于处理规则引擎相关的异常情况
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
public class RuleEngineException extends RuntimeException {
    /**
     * 错误代码
     */
    private final String errorCode;

    /**
     * 构造函数
     * @param message 错误信息
     */
    public RuleEngineException(String message) {
        super(message);
        this.errorCode = "RE-001";
    }

    /**
     * 构造函数
     * @param message 错误信息
     * @param cause 原始异常
     */
    public RuleEngineException(String message, Throwable cause) {
        super(message, cause);
        this.errorCode = "RE-001";
    }

    /**
     * 构造函数
     * @param message 错误信息
     * @param errorCode 错误代码
     */
    public RuleEngineException(String message, String errorCode) {
        super(message);
        this.errorCode = errorCode;
    }

    /**
     * 构造函数
     * @param message 错误信息
     * @param cause 原始异常
     * @param errorCode 错误代码
     */
    public RuleEngineException(String message, Throwable cause, String errorCode) {
        super(message, cause);
        this.errorCode = errorCode;
    }

    /**
     * 获取错误代码
     */
    public String getErrorCode() {
        return errorCode;
    }

    /**
     * 规则加载异常
     */
    public static class RuleLoadException extends RuleEngineException {
        public RuleLoadException(String message) {
            super(message, "RE-101");
        }

        public RuleLoadException(String message, Throwable cause) {
            super(message, cause, "RE-101");
        }
    }

    /**
     * 规则编译异常
     */
    public static class RuleCompileException extends RuleEngineException {
        public RuleCompileException(String message) {
            super(message, "RE-102");
        }

        public RuleCompileException(String message, Throwable cause) {
            super(message, cause, "RE-102");
        }
    }

    /**
     * 规则执行异常
     */
    public static class RuleExecutionException extends RuleEngineException {
        public RuleExecutionException(String message) {
            super(message, "RE-103");
        }

        public RuleExecutionException(String message, Throwable cause) {
            super(message, cause, "RE-103");
        }
    }

    /**
     * 规则验证异常
     */
    public static class RuleValidationException extends RuleEngineException {
        public RuleValidationException(String message) {
            super(message, "RE-104");
        }

        public RuleValidationException(String message, Throwable cause) {
            super(message, cause, "RE-104");
        }
    }
} 