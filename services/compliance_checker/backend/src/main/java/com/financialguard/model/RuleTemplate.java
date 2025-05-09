package com.financialguard.model;

import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.Data;

/**
 * 规则模板模型类
 * 用于管理和存储规则模板
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Data
@Entity
@Table(name = "rule_templates")
public class RuleTemplate {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 模板编码
     */
    @Column(nullable = false, unique = true)
    private String code;

    /**
     * 模板名称
     */
    @Column(nullable = false)
    private String name;

    /**
     * 模板描述
     */
    @Column(length = 1000)
    private String description;

    /**
     * 模板类型（费用类/收入类/关联交易类等）
     */
    @Column(nullable = false)
    private String type;

    /**
     * 规则模板内容（Drools DRL格式）
     */
    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    /**
     * 默认严重程度
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RuleSeverity defaultSeverity;

    /**
     * 适用的会计准则（GAAP/IFRS）
     */
    @Column(nullable = false)
    private String accountingStandard;

    /**
     * 参数定义（JSON格式）
     * 例如：{"threshold": "阈值", "period": "统计周期"}
     */
    @Column(columnDefinition = "TEXT")
    private String parameters;

    /**
     * 模板状态（启用/禁用）
     */
    @Column(nullable = false)
    private boolean enabled = true;

    /**
     * 版本号
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
     * 法规依据
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

    /**
     * 根据参数生成规则实例
     * 
     * @param parameters 规则参数
     * @return 规则内容
     */
    public String generateRule(String parameters) {
        // TODO: 实现参数替换逻辑
        return content.replace("${parameters}", parameters);
    }
} 