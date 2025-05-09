package com.financialguard.model;

import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * 规则执行日志模型类
 * 记录规则执行的详细信息
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Data
@Entity
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "rule_execution_logs")
public class RuleExecutionLog {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 规则编码
     */
    @Column(nullable = false)
    private String ruleCode;

    /**
     * 规则名称
     */
    @Column(nullable = false)
    private String ruleName;

    /**
     * 执行开始时间
     */
    @Column(nullable = false)
    private LocalDateTime startTime;

    /**
     * 执行结束时间
     */
    @Column(nullable = false)
    private LocalDateTime endTime;

    /**
     * 执行耗时（毫秒）
     */
    @Column(nullable = false)
    private Long duration;

    /**
     * 执行状态（成功/失败）
     */
    @Column(nullable = false)
    private String status;

    /**
     * 执行结果
     */
    @Column(length = 2000)
    private String result;

    /**
     * 错误信息
     */
    @Column(length = 2000)
    private String errorMessage;

    /**
     * 输入参数（JSON格式）
     */
    @Column(columnDefinition = "TEXT")
    private String inputParams;

    /**
     * 执行人
     */
    @Column(nullable = false)
    private String executor;

    /**
     * 执行环境（开发/测试/生产）
     */
    @Column(nullable = false)
    private String environment;

    /**
     * 规则版本
     */
    private String ruleVersion;

    /**
     * 业务ID
     */
    private String businessId;

    /**
     * 业务类型
     */
    private String businessType;

    /**
     * 创建时间
     */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    /**
     * 计算执行耗时
     */
    public void calculateDuration() {
        if (startTime != null && endTime != null) {
            duration = java.time.Duration.between(startTime, endTime).toMillis();
        }
    }

    /**
     * 设置执行失败信息
     * 
     * @param errorMessage 错误信息
     */
    public void setFailure(String errorMessage) {
        this.status = "失败";
        this.errorMessage = errorMessage;
        this.endTime = LocalDateTime.now();
        calculateDuration();
    }

    /**
     * 设置执行成功信息
     * 
     * @param result 执行结果
     */
    public void setSuccess(String result) {
        this.status = "成功";
        this.result = result;
        this.endTime = LocalDateTime.now();
        calculateDuration();
    }
} 