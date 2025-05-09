package com.financialguard.repository;

import com.financialguard.model.AuditReport;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

/**
 * 审计报告数据访问接口
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Repository
public interface AuditReportRepository extends JpaRepository<AuditReport, Long> {
    
    /**
     * 根据报告编号查询
     * 
     * @param reportNo 报告编号
     * @return 报告对象
     */
    Optional<AuditReport> findByReportNo(String reportNo);

    /**
     * 根据报告状态查询
     * 
     * @param status 报告状态
     * @param pageable 分页参数
     * @return 报告分页结果
     */
    Page<AuditReport> findByStatusOrderByCreatedAtDesc(String status, Pageable pageable);

    /**
     * 查询指定时间范围内的报告
     * 
     * @param startDate 开始时间
     * @param endDate 结束时间
     * @param pageable 分页参数
     * @return 报告分页结果
     */
    Page<AuditReport> findByAuditStartDateBetweenOrderByCreatedAtDesc(
            LocalDateTime startDate, LocalDateTime endDate, Pageable pageable);

    /**
     * 根据审计执行人查询
     * 
     * @param auditor 审计执行人
     * @param pageable 分页参数
     * @return 报告分页结果
     */
    Page<AuditReport> findByAuditorOrderByCreatedAtDesc(String auditor, Pageable pageable);

    /**
     * 根据风险等级查询
     * 
     * @param riskLevel 风险等级
     * @param pageable 分页参数
     * @return 报告分页结果
     */
    Page<AuditReport> findByRiskLevelOrderByCreatedAtDesc(String riskLevel, Pageable pageable);

    /**
     * 删除报告
     * 
     * @param reportNo 报告编号
     * @return 删除的数量
     */
    long deleteByReportNo(String reportNo);
} 