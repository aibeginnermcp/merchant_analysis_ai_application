package com.guardian.audit.model;

/**
 * 审计结果状态枚举
 * 用于标识审计问题的处理状态
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
public enum AuditResultStatus {
    /**
     * 待处理
     * 新发现的问题，尚未开始处理
     */
    PENDING("待处理", "问题待分派责任人处理"),

    /**
     * 处理中
     * 问题已分派，正在处理过程中
     */
    IN_PROGRESS("处理中", "问题正在处理中"),

    /**
     * 待复核
     * 问题处理完成，等待复核确认
     */
    PENDING_REVIEW("待复核", "处理结果等待复核确认"),

    /**
     * 已解决
     * 问题已处理完成并通过复核
     */
    RESOLVED("已解决", "问题已处理完成并确认"),

    /**
     * 已关闭
     * 问题已处理完成并归档
     */
    CLOSED("已关闭", "问题已处理完成并归档"),

    /**
     * 已驳回
     * 处理结果未通过复核，需要重新处理
     */
    REJECTED("已驳回", "处理结果未通过复核"),

    /**
     * 已取消
     * 经确认不需要处理的问题
     */
    CANCELLED("已取消", "确认无需处理"),

    /**
     * 已过期
     * 未在规定时间内处理完成
     */
    EXPIRED("已过期", "未在规定时间内处理");

    /**
     * 状态名称
     */
    private final String name;

    /**
     * 状态描述
     */
    private final String description;

    AuditResultStatus(String name, String description) {
        this.name = name;
        this.description = description;
    }

    /**
     * 获取状态名称
     */
    public String getName() {
        return name;
    }

    /**
     * 获取状态描述
     */
    public String getDescription() {
        return description;
    }

    /**
     * 判断是否为终态
     */
    public boolean isFinalState() {
        return this == RESOLVED || this == CLOSED || this == CANCELLED;
    }

    /**
     * 判断是否需要处理
     */
    public boolean needsAction() {
        return this == PENDING || this == IN_PROGRESS || this == REJECTED;
    }

    /**
     * 判断是否可以修改
     */
    public boolean isModifiable() {
        return !isFinalState() && this != EXPIRED;
    }

    /**
     * 获取下一个可能的状态列表
     */
    public AuditResultStatus[] getNextPossibleStates() {
        switch (this) {
            case PENDING:
                return new AuditResultStatus[]{IN_PROGRESS, CANCELLED};
            case IN_PROGRESS:
                return new AuditResultStatus[]{PENDING_REVIEW, CANCELLED};
            case PENDING_REVIEW:
                return new AuditResultStatus[]{RESOLVED, REJECTED};
            case REJECTED:
                return new AuditResultStatus[]{IN_PROGRESS, CANCELLED};
            case RESOLVED:
                return new AuditResultStatus[]{CLOSED};
            default:
                return new AuditResultStatus[]{};
        }
    }
} 