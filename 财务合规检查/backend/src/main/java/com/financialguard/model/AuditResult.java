package com.financialguard.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import javax.persistence.*;
import lombok.Data;

/**
 * 审计结果模型类
 * 存储规则执行的结果信息
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Data
@Entity
@Table(name = "audit_results")
public class AuditResult {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 关联的审计规则
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "rule_id", nullable = false)
    private AuditRule rule;

    /**
     * 审计结果状态
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AuditResultStatus status;

    /**
     * 审计发现的问题描述
     */
    @Column(length = 2000)
    private String findings;

    /**
     * 建议的整改措施
     */
    @Column(length = 1000)
    private String recommendations;

    /**
     * 相关的业务数据ID列表（JSON格式）
     */
    @Column(columnDefinition = "TEXT")
    private String relatedDataIds;

    /**
     * 审计证据列表
     */
    @ElementCollection
    @CollectionTable(name = "audit_evidences", 
        joinColumns = @JoinColumn(name = "result_id"))
    private List<String> evidences = new ArrayList<>();

    /**
     * 执行时间
     */
    @Column(nullable = false)
    private LocalDateTime executedAt;

    /**
     * 执行人
     */
    @Column(nullable = false)
    private String executedBy;

    /**
     * 审核状态（待审核/已审核/已驳回）
     */
    @Column(nullable = false)
    private String reviewStatus = "待审核";

    /**
     * 审核人
     */
    private String reviewedBy;

    /**
     * 审核时间
     */
    private LocalDateTime reviewedAt;

    /**
     * 审核意见
     */
    @Column(length = 1000)
    private String reviewComments;

    @PrePersist
    protected void onCreate() {
        executedAt = LocalDateTime.now();
    }

    /**
     * 添加审计证据
     * 
     * @param evidence 证据路径或描述
     */
    public void addEvidence(String evidence) {
        if (evidences == null) {
            evidences = new ArrayList<>();
        }
        evidences.add(evidence);
    }

    /**
     * 设置审核结果
     * 
     * @param reviewedBy 审核人
     * @param status 审核状态
     * @param comments 审核意见
     */
    public void setReviewResult(String reviewedBy, String status, String comments) {
        this.reviewedBy = reviewedBy;
        this.reviewStatus = status;
        this.reviewComments = comments;
        this.reviewedAt = LocalDateTime.now();
    }
} 