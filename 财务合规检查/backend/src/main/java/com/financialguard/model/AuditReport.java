package com.financialguard.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import javax.persistence.*;
import lombok.Data;

/**
 * 审计报告模型类
 * 存储审计报告的基本信息和内容
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Data
@Entity
@Table(name = "audit_reports")
public class AuditReport {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 报告编号
     */
    @Column(nullable = false, unique = true)
    private String reportNo;

    /**
     * 报告标题
     */
    @Column(nullable = false)
    private String title;

    /**
     * 审计期间（起始日期）
     */
    @Column(nullable = false)
    private LocalDateTime auditStartDate;

    /**
     * 审计期间（结束日期）
     */
    @Column(nullable = false)
    private LocalDateTime auditEndDate;

    /**
     * 审计范围
     */
    @Column(length = 1000)
    private String auditScope;

    /**
     * 审计发现（JSON格式）
     */
    @Column(columnDefinition = "TEXT")
    private String findings;

    /**
     * 风险等级
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RuleSeverity riskLevel;

    /**
     * 整改建议
     */
    @Column(columnDefinition = "TEXT")
    private String recommendations;

    /**
     * 报告状态（草稿/待审核/已审核/已发布）
     */
    @Column(nullable = false)
    private String status = "草稿";

    /**
     * 审计执行人
     */
    @Column(nullable = false)
    private String auditor;

    /**
     * 审核人
     */
    private String reviewer;

    /**
     * 审核意见
     */
    @Column(length = 1000)
    private String reviewComments;

    /**
     * 审核时间
     */
    private LocalDateTime reviewedAt;

    /**
     * 相关规则列表
     */
    @ElementCollection
    @CollectionTable(name = "report_rules", 
        joinColumns = @JoinColumn(name = "report_id"))
    private List<String> relatedRules = new ArrayList<>();

    /**
     * 附件列表（JSON格式）
     */
    @Column(columnDefinition = "TEXT")
    private String attachments;

    /**
     * 创建时间
     */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /**
     * 最后修改时间
     */
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    /**
     * 创建人
     */
    @Column(nullable = false, updatable = false)
    private String createdBy;

    /**
     * 最后修改人
     */
    @Column(nullable = false)
    private String updatedBy;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * 添加相关规则
     * 
     * @param ruleCode 规则编码
     */
    public void addRelatedRule(String ruleCode) {
        if (relatedRules == null) {
            relatedRules = new ArrayList<>();
        }
        if (!relatedRules.contains(ruleCode)) {
            relatedRules.add(ruleCode);
        }
    }

    /**
     * 设置审核结果
     * 
     * @param reviewer 审核人
     * @param status 审核状态
     * @param comments 审核意见
     */
    public void setReviewResult(String reviewer, String status, String comments) {
        this.reviewer = reviewer;
        this.status = status;
        this.reviewComments = comments;
        this.reviewedAt = LocalDateTime.now();
    }

    /**
     * 生成报告编号
     */
    public void generateReportNo() {
        this.reportNo = String.format("AR%s%06d",
                LocalDateTime.now().format(java.time.format.DateTimeFormatter.BASIC_ISO_DATE),
                System.nanoTime() % 1000000);
    }
} 