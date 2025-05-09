package com.financialguard.model;

/**
 * 规则严重程度枚举
 * 定义了审计规则的风险等级
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
public enum RuleSeverity {
    
    /**
     * 高危风险
     * 需要立即处理，可能造成重大财务损失或合规问题
     */
    HIGH("高危", "需要立即处理，可能造成重大财务损失或合规问题"),

    /**
     * 中度风险
     * 需要及时处理，可能影响财务报告的准确性
     */
    MEDIUM("中危", "需要及时处理，可能影响财务报告的准确性"),

    /**
     * 低度风险
     * 需要关注，但不会造成重大影响
     */
    LOW("低危", "需要关注，但不会造成重大影响"),

    /**
     * 提示信息
     * 仅作为提醒，不构成实际风险
     */
    INFO("提示", "仅作为提醒，不构成实际风险");

    private final String label;
    private final String description;

    RuleSeverity(String label, String description) {
        this.label = label;
        this.description = description;
    }

    public String getLabel() {
        return label;
    }

    public String getDescription() {
        return description;
    }

    /**
     * 根据标签获取严重程度枚举
     * 
     * @param label 严重程度标签
     * @return 对应的严重程度枚举值
     */
    public static RuleSeverity fromLabel(String label) {
        for (RuleSeverity severity : values()) {
            if (severity.label.equals(label)) {
                return severity;
            }
        }
        throw new IllegalArgumentException("未知的严重程度标签: " + label);
    }
} 