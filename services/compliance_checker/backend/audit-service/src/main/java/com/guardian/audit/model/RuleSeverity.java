package com.guardian.audit.model;

/**
 * 规则严重程度枚举
 * 用于标识规则违反的严重程度
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
public enum RuleSeverity {
    /**
     * 致命
     * 可能导致重大财务风险或违法违规的问题
     * 需要立即处理并上报高层管理人员
     */
    CRITICAL(1, "致命"),

    /**
     * 高危
     * 存在显著财务风险或合规隐患
     * 需要优先处理
     */
    HIGH(2, "高危"),

    /**
     * 中危
     * 存在潜在风险，但不会立即造成重大影响
     * 需要在计划内处理
     */
    MEDIUM(3, "中危"),

    /**
     * 低危
     * 轻微问题或最佳实践建议
     * 可以在常规工作中逐步改进
     */
    LOW(4, "低危"),

    /**
     * 提示
     * 仅作为提醒或建议
     * 不强制要求处理
     */
    INFO(5, "提示");

    /**
     * 严重程度级别
     * 数字越小表示严重程度越高
     */
    private final int level;

    /**
     * 严重程度描述
     */
    private final String description;

    RuleSeverity(int level, String description) {
        this.level = level;
        this.description = description;
    }

    /**
     * 获取严重程度级别
     */
    public int getLevel() {
        return level;
    }

    /**
     * 获取严重程度描述
     */
    public String getDescription() {
        return description;
    }

    /**
     * 判断是否需要立即处理
     */
    public boolean requiresImmediateAction() {
        return this == CRITICAL || this == HIGH;
    }

    /**
     * 判断是否需要上报
     */
    public boolean requiresEscalation() {
        return this == CRITICAL;
    }

    /**
     * 获取处理时限（小时）
     */
    public int getHandlingTimeLimit() {
        switch (this) {
            case CRITICAL:
                return 4;  // 4小时内必须处理
            case HIGH:
                return 24; // 24小时内必须处理
            case MEDIUM:
                return 72; // 3天内处理
            case LOW:
                return 168; // 7天内处理
            case INFO:
                return 720; // 30天内处理
            default:
                return 0;
        }
    }
} 