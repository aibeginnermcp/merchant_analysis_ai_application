package com.guardian.audit.model;

import lombok.Builder;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.time.temporal.ChronoUnit;

/**
 * 审计结果模型类
 * 用于记录规则执行的结果和相关信息
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
@Data
@Builder
public class AuditResult {
    /**
     * 结果ID
     * 用于唯一标识一个审计结果
     */
    private String id;
    
    /**
     * 触发规则
     * 导致该结果的审计规则
     */
    private AuditRule rule;
    
    /**
     * 检查时间
     * 规则执行的时间点
     */
    private LocalDateTime checkTime;
    
    /**
     * 严重程度
     * 继承自规则定义的严重程度
     */
    private RuleSeverity severity;
    
    /**
     * 检查结果
     * true表示通过检查，false表示存在问题
     */
    private boolean passed;
    
    /**
     * 问题描述
     * 详细说明发现的问题
     */
    private String description;
    
    /**
     * 影响对象
     * 受影响的业务对象（如：凭证号、科目等）
     */
    private Map<String, Object> affectedObjects;
    
    /**
     * 证据清单
     * 支持审计结果的相关证据
     */
    private List<AuditEvidence> evidences;
    
    /**
     * 处理建议
     * 系统给出的处理建议
     */
    private List<String> recommendations;
    
    /**
     * 处理状态
     * 记录问题的处理进展
     */
    private AuditResultStatus status;
    
    /**
     * 处理记录
     * 记录问题处理的过程和结果
     */
    private List<AuditResultHandling> handlingRecords;
    
    /**
     * 处理期限
     * 问题需要处理的截止时间
     */
    private LocalDateTime deadline;
    
    /**
     * 责任人
     * 负责处理该问题的人员
     */
    private String assignee;
    
    /**
     * 审计结果处理记录
     * 内部类，用于记录问题处理的历史
     */
    @Data
    @Builder
    public static class AuditResultHandling {
        /**
         * 处理时间
         */
        private LocalDateTime handleTime;
        
        /**
         * 处理人
         */
        private String handler;
        
        /**
         * 处理动作
         */
        private String action;
        
        /**
         * 处理说明
         */
        private String comment;
        
        /**
         * 相关附件
         */
        private List<String> attachments;
    }
    
    /**
     * 审计证据
     * 内部类，用于记录支持审计结果的证据
     */
    @Data
    @Builder
    public static class AuditEvidence {
        /**
         * 证据类型
         */
        private String type;
        
        /**
         * 证据来源
         */
        private String source;
        
        /**
         * 证据内容
         */
        private Object content;
        
        /**
         * 证据hash
         * 用于确保证据的完整性
         */
        private String hash;
        
        /**
         * 采集时间
         */
        private LocalDateTime collectTime;
        
        /**
         * 采集人
         */
        private String collector;
    }
    
    /**
     * 计算处理期限
     * 根据严重程度自动计算处理期限
     */
    public void calculateDeadline() {
        if (checkTime != null && severity != null) {
            int hours = severity.getHandlingTimeLimit();
            this.deadline = checkTime.plusHours(hours);
        }
    }
    
    /**
     * 添加处理记录
     */
    public void addHandlingRecord(AuditResultHandling record) {
        if (handlingRecords == null) {
            handlingRecords = new ArrayList<>();
        }
        handlingRecords.add(record);
        
        // 更新处理状态
        if (status == AuditResultStatus.PENDING) {
            status = AuditResultStatus.IN_PROGRESS;
        }
    }
    
    /**
     * 判断是否超期
     */
    public boolean isOverdue() {
        return deadline != null && 
               LocalDateTime.now().isAfter(deadline) && 
               status != AuditResultStatus.RESOLVED;
    }
    
    /**
     * 获取剩余处理时间（小时）
     */
    public long getRemainingHours() {
        if (deadline == null) {
            return 0;
        }
        return ChronoUnit.HOURS.between(LocalDateTime.now(), deadline);
    }
} 