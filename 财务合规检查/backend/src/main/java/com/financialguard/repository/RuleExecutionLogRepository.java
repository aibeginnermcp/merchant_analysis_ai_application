package com.financialguard.repository;

import com.financialguard.model.RuleExecutionLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;

/**
 * 规则执行日志数据访问接口
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Repository
public interface RuleExecutionLogRepository extends JpaRepository<RuleExecutionLog, Long> {
    
    /**
     * 根据规则编码查询执行日志
     * 
     * @param ruleCode 规则编码
     * @param pageable 分页参数
     * @return 日志分页结果
     */
    Page<RuleExecutionLog> findByRuleCodeOrderByStartTimeDesc(String ruleCode, Pageable pageable);

    /**
     * 查询指定时间范围内的执行日志
     * 
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @param pageable 分页参数
     * @return 日志分页结果
     */
    Page<RuleExecutionLog> findByStartTimeBetweenOrderByStartTimeDesc(
            LocalDateTime startTime, LocalDateTime endTime, Pageable pageable);

    /**
     * 根据执行状态查询日志
     * 
     * @param status 执行状态
     * @param pageable 分页参数
     * @return 日志分页结果
     */
    Page<RuleExecutionLog> findByStatusOrderByStartTimeDesc(String status, Pageable pageable);

    /**
     * 统计规则执行次数
     * 
     * @param ruleCode 规则编码
     * @return 执行次数
     */
    long countByRuleCode(String ruleCode);

    /**
     * 统计规则执行状态
     * 
     * @param ruleCode 规则编码
     * @param status 执行状态
     * @return 状态数量
     */
    long countByRuleCodeAndStatus(String ruleCode, String status);

    /**
     * 计算规则平均执行时间
     * 
     * @param ruleCode 规则编码
     * @return 平均执行时间
     */
    @Query("SELECT AVG(l.duration) FROM RuleExecutionLog l WHERE l.ruleCode = ?1")
    double averageDurationByRuleCode(String ruleCode);

    /**
     * 删除过期日志
     * 
     * @param expirationTime 过期时间
     * @return 删除的日志数量
     */
    long deleteByStartTimeBefore(LocalDateTime expirationTime);
} 