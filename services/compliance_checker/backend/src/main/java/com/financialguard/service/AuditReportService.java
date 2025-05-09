package com.financialguard.service;

import com.financialguard.model.AuditReport;
import com.financialguard.model.RuleExecutionLog;
import com.financialguard.repository.AuditReportRepository;
import com.financialguard.repository.RuleExecutionLogRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 审计报告服务类
 * 实现报告的生成和管理功能
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Service
public class AuditReportService {
    
    private static final Logger logger = LoggerFactory.getLogger(AuditReportService.class);
    private final AuditReportRepository reportRepository;
    private final RuleExecutionLogRepository logRepository;
    private final ObjectMapper objectMapper;

    @Autowired
    public AuditReportService(
            AuditReportRepository reportRepository,
            RuleExecutionLogRepository logRepository,
            ObjectMapper objectMapper) {
        this.reportRepository = reportRepository;
        this.logRepository = logRepository;
        this.objectMapper = objectMapper;
    }

    /**
     * 生成审计报告
     * 
     * @param startDate 审计开始日期
     * @param endDate 审计结束日期
     * @param auditor 审计执行人
     * @return 生成的报告
     */
    @Transactional
    public AuditReport generateReport(LocalDateTime startDate, LocalDateTime endDate, String auditor) {
        logger.info("开始生成审计报告，审计期间: {} - {}", startDate, endDate);
        
        // 查询审计期间的执行日志
        List<RuleExecutionLog> logs = logRepository
                .findByStartTimeBetweenOrderByStartTimeDesc(startDate, endDate, Pageable.unpaged())
                .getContent();
        
        // 创建报告
        AuditReport report = new AuditReport();
        report.generateReportNo();
        report.setTitle(String.format("财务合规审计报告 (%s - %s)",
                startDate.toLocalDate(), endDate.toLocalDate()));
        report.setAuditStartDate(startDate);
        report.setAuditEndDate(endDate);
        report.setAuditor(auditor);
        
        // 分析审计发现
        Map<String, Object> findings = analyzeFindings(logs);
        try {
            report.setFindings(objectMapper.writeValueAsString(findings));
        } catch (Exception e) {
            logger.error("审计发现序列化失败: {}", e.getMessage());
        }
        
        // 设置风险等级
        report.setRiskLevel(calculateRiskLevel(findings));
        
        // 生成整改建议
        report.setRecommendations(generateRecommendations(findings));
        
        // 添加相关规则
        logs.stream()
                .map(RuleExecutionLog::getRuleCode)
                .distinct()
                .forEach(report::addRelatedRule);
        
        return reportRepository.save(report);
    }

    /**
     * 分析审计发现
     * 
     * @param logs 执行日志列表
     * @return 审计发现
     */
    private Map<String, Object> analyzeFindings(List<RuleExecutionLog> logs) {
        Map<String, Object> findings = new HashMap<>();
        
        // 按规则分组统计
        Map<String, List<RuleExecutionLog>> ruleGroups = logs.stream()
                .collect(Collectors.groupingBy(RuleExecutionLog::getRuleCode));
        
        // 分析每个规则的执行情况
        ruleGroups.forEach((ruleCode, ruleLogs) -> {
            Map<String, Object> ruleFinding = new HashMap<>();
            
            // 统计执行次数
            long totalCount = ruleLogs.size();
            long failureCount = ruleLogs.stream()
                    .filter(log -> "失败".equals(log.getStatus()))
                    .count();
            
            ruleFinding.put("totalExecutions", totalCount);
            ruleFinding.put("failureCount", failureCount);
            ruleFinding.put("failureRate", (double) failureCount / totalCount);
            
            // 收集具体问题
            List<Map<String, String>> issues = ruleLogs.stream()
                    .filter(log -> "失败".equals(log.getStatus()))
                    .map(log -> {
                        Map<String, String> issue = new HashMap<>();
                        issue.put("time", log.getStartTime().toString());
                        issue.put("description", log.getErrorMessage());
                        return issue;
                    })
                    .collect(Collectors.toList());
            
            ruleFinding.put("issues", issues);
            findings.put(ruleCode, ruleFinding);
        });
        
        return findings;
    }

    /**
     * 计算整体风险等级
     * 
     * @param findings 审计发现
     * @return 风险等级
     */
    private RuleSeverity calculateRiskLevel(Map<String, Object> findings) {
        // 计算失败率
        double totalFailureRate = findings.values().stream()
                .map(finding -> (Map<String, Object>) finding)
                .mapToDouble(finding -> (double) finding.get("failureRate"))
                .average()
                .orElse(0.0);
        
        // 根据失败率确定风险等级
        if (totalFailureRate > 0.3) {
            return RuleSeverity.HIGH;
        } else if (totalFailureRate > 0.1) {
            return RuleSeverity.MEDIUM;
        } else if (totalFailureRate > 0.05) {
            return RuleSeverity.LOW;
        } else {
            return RuleSeverity.INFO;
        }
    }

    /**
     * 生成整改建议
     * 
     * @param findings 审计发现
     * @return 整改建议
     */
    private String generateRecommendations(Map<String, Object> findings) {
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("根据审计发现，建议采取以下整改措施：\n\n");
        
        findings.forEach((ruleCode, finding) -> {
            Map<String, Object> ruleFinding = (Map<String, Object>) finding;
            double failureRate = (double) ruleFinding.get("failureRate");
            
            if (failureRate > 0.1) {
                recommendations.append(String.format("1. 针对规则 %s：\n", ruleCode));
                recommendations.append(String.format("   - 当前失败率：%.2f%%\n", failureRate * 100));
                recommendations.append("   - 建议措施：\n");
                recommendations.append("     * 复查相关业务流程\n");
                recommendations.append("     * 加强人员培训\n");
                recommendations.append("     * 完善内控制度\n\n");
            }
        });
        
        return recommendations.toString();
    }

    /**
     * 更新报告状态
     * 
     * @param reportNo 报告编号
     * @param status 新状态
     * @param reviewer 审核人
     * @param comments 审核意见
     */
    @Transactional
    public void updateReportStatus(String reportNo, String status, String reviewer, String comments) {
        reportRepository.findByReportNo(reportNo).ifPresent(report -> {
            report.setReviewResult(reviewer, status, comments);
            reportRepository.save(report);
            logger.info("更新报告状态完成: {}", reportNo);
        });
    }

    /**
     * 查询报告
     * 
     * @param pageable 分页参数
     * @return 报告分页结果
     */
    public Page<AuditReport> findReports(Pageable pageable) {
        return reportRepository.findAll(pageable);
    }

    /**
     * 根据报告编号查询
     * 
     * @param reportNo 报告编号
     * @return 报告对象
     */
    public Optional<AuditReport> findByReportNo(String reportNo) {
        return reportRepository.findByReportNo(reportNo);
    }

    /**
     * 删除报告
     * 
     * @param reportNo 报告编号
     */
    @Transactional
    public void deleteReport(String reportNo) {
        reportRepository.deleteByReportNo(reportNo);
        logger.info("删除报告完成: {}", reportNo);
    }
} 