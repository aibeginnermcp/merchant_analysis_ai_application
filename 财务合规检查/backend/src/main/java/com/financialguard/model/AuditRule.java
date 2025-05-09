package com.financialguard.model;

import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.Data;

/**
 * 审计规则模型类
 * 定义了单个审计规则的属性和行为
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Data
@Entity
@Table(name = "audit_rules")
public class AuditRule {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 规则编码，例如：FIN-101
     */
    @Column(nullable = false, unique = true)
    private String code;

    /**
     * 规则名称
     */
    @Column(nullable = false)
    private String name;

    /**
     * 规则描述
     */
    @Column(length = 1000)
    private String description;

    /**
     * 规则内容（Drools DRL格式）
     */
    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    /**
     * 规则严重程度
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RuleSeverity severity;

    /**
     * 规则状态（启用/禁用）
     */
    @Column(nullable = false)
    private boolean enabled = true;

    /**
     * 规则版本号
     */
    @Version
    private Long version;

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

    /**
     * 规则引用的法规依据
     */
    @Column(length = 500)
    private String references;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
} 