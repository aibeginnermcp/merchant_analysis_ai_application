package com.financialguard.model;

import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * 审计告警模型类
 * 存储规则触发的告警信息
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Data
@Entity
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "audit_alerts")
public class AuditAlert {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 告警严重程度
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RuleSeverity severity;

    /**
     * 告警消息
     */
    @Column(nullable = false, length = 1000)
    private String message;

    /**
     * 告警时间
     */
    @Column(nullable = false)
    private LocalDateTime alertTime;

    /**
     * 告警状态（未处理/处理中/已处理/已关闭）
     */
    @Column(nullable = false)
    private String status = "未处理";

    /**
     * 处理人
     */
    private String handler;

    /**
     * 处理时间
     */
    private LocalDateTime handleTime;

    /**
     * 处理意见
     */
    @Column(length = 1000)
    private String handleComments;

    /**
     * 关联的业务ID
     */
    private String businessId;

    /**
     * 创建告警
     * 
     * @param severity 严重程度
     * @param message 告警消息
     */
    public AuditAlert(RuleSeverity severity, String message) {
        this.severity = severity;
        this.message = message;
        this.alertTime = LocalDateTime.now();
    }

    /**
     * 处理告警
     * 
     * @param handler 处理人
     * @param status 处理状态
     * @param comments 处理意见
     */
    public void handle(String handler, String status, String comments) {
        this.handler = handler;
        this.status = status;
        this.handleComments = comments;
        this.handleTime = LocalDateTime.now();
    }

    /**
     * 关闭告警
     * 
     * @param handler 处理人
     * @param comments 关闭原因
     */
    public void close(String handler, String comments) {
        handle(handler, "已关闭", comments);
    }
} 