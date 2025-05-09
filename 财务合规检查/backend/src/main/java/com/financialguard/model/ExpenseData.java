package com.financialguard.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import javax.persistence.*;
import lombok.Data;

/**
 * 费用数据模型类
 * 存储待审计的费用信息
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Data
@Entity
@Table(name = "expense_data")
public class ExpenseData {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 费用类型（促销费用/差旅费用/招待费用等）
     */
    @Column(nullable = false)
    private String type;

    /**
     * 费用金额
     */
    @Column(nullable = false, precision = 20, scale = 2)
    private BigDecimal amount;

    /**
     * 费用发生日期
     */
    @Column(nullable = false)
    private LocalDate expenseDate;

    /**
     * 费用所属部门
     */
    @Column(nullable = false)
    private String department;

    /**
     * 费用说明
     */
    @Column(length = 1000)
    private String explanation;

    /**
     * 关联的GMV（用于计算费用率）
     */
    @Column(precision = 20, scale = 2)
    private BigDecimal gmv;

    /**
     * 预算金额
     */
    @Column(precision = 20, scale = 2)
    private BigDecimal budgetAmount;

    /**
     * 审批状态
     */
    @Column(nullable = false)
    private String approvalStatus = "待审批";

    /**
     * 审批人
     */
    private String approver;

    /**
     * 审批意见
     */
    @Column(length = 500)
    private String approvalComments;

    /**
     * 关联的凭证号
     */
    private String voucherNo;

    /**
     * 创建时间
     */
    @Column(nullable = false, updatable = false)
    private LocalDate createdAt;

    /**
     * 创建人
     */
    @Column(nullable = false, updatable = false)
    private String createdBy;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
    }

    /**
     * 计算费用率
     * 
     * @return 费用率（费用金额/GMV）
     */
    public BigDecimal calculateExpenseRate() {
        if (gmv == null || gmv.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        return amount.divide(gmv, 4, BigDecimal.ROUND_HALF_UP);
    }

    /**
     * 检查是否超预算
     * 
     * @return 是否超预算
     */
    public boolean isOverBudget() {
        if (budgetAmount == null) {
            return false;
        }
        return amount.compareTo(budgetAmount) > 0;
    }

    /**
     * 计算超预算金额
     * 
     * @return 超预算金额
     */
    public BigDecimal getOverBudgetAmount() {
        if (!isOverBudget()) {
            return BigDecimal.ZERO;
        }
        return amount.subtract(budgetAmount);
    }
} 