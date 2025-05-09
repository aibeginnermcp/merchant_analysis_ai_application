package com.guardian.audit.controller;

import com.guardian.audit.model.AuditRule;
import com.guardian.audit.service.RuleEngineService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.Collection;

/**
 * 规则管理控制器
 * 提供规则的查询、启用/禁用等管理功能
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
@Tag(name = "规则管理", description = "提供规则的查询、启用/禁用等管理功能")
@RestController
@RequestMapping("/api/v1/rules")
@Validated
public class RuleController {

    private final RuleEngineService ruleEngineService;

    @Autowired
    public RuleController(RuleEngineService ruleEngineService) {
        this.ruleEngineService = ruleEngineService;
    }

    /**
     * 获取所有规则
     */
    @Operation(summary = "获取所有规则", description = "获取系统中所有已加载的规则")
    @GetMapping
    public ResponseEntity<Collection<AuditRule>> getAllRules() {
        return ResponseEntity.ok(ruleEngineService.getAllRules());
    }

    /**
     * 根据ID获取规则
     */
    @Operation(summary = "获取规则详情", description = "根据规则ID获取规则详细信息")
    @GetMapping("/{ruleId}")
    public ResponseEntity<AuditRule> getRuleById(
            @Parameter(description = "规则ID", example = "EXPENSE-PROMO-001")
            @PathVariable String ruleId) {
        return ruleEngineService.getRuleById(ruleId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * 启用规则
     */
    @Operation(summary = "启用规则", description = "启用指定的规则")
    @PostMapping("/{ruleId}/enable")
    public ResponseEntity<Void> enableRule(
            @Parameter(description = "规则ID", example = "EXPENSE-PROMO-001")
            @PathVariable String ruleId) {
        ruleEngineService.getRuleById(ruleId)
                .ifPresent(rule -> {
                    rule.setEnabled(true);
                    // TODO: 保存规则状态
                });
        return ResponseEntity.ok().build();
    }

    /**
     * 禁用规则
     */
    @Operation(summary = "禁用规则", description = "禁用指定的规则")
    @PostMapping("/{ruleId}/disable")
    public ResponseEntity<Void> disableRule(
            @Parameter(description = "规则ID", example = "EXPENSE-PROMO-001")
            @PathVariable String ruleId) {
        ruleEngineService.getRuleById(ruleId)
                .ifPresent(rule -> {
                    rule.setEnabled(false);
                    // TODO: 保存规则状态
                });
        return ResponseEntity.ok().build();
    }

    /**
     * 获取规则执行历史
     */
    @Operation(summary = "获取规则执行历史", description = "获取指定规则的执行历史记录")
    @GetMapping("/{ruleId}/history")
    public ResponseEntity<Object> getRuleHistory(
            @Parameter(description = "规则ID", example = "EXPENSE-PROMO-001")
            @PathVariable String ruleId,
            @Parameter(description = "开始时间", example = "2024-03-01")
            @RequestParam(required = false) String startDate,
            @Parameter(description = "结束时间", example = "2024-03-31")
            @RequestParam(required = false) String endDate) {
        // TODO: 实现规则执行历史查询
        return ResponseEntity.ok().build();
    }

    /**
     * 获取规则统计信息
     */
    @Operation(summary = "获取规则统计信息", description = "获取规则执行的统计信息")
    @GetMapping("/{ruleId}/stats")
    public ResponseEntity<Object> getRuleStats(
            @Parameter(description = "规则ID", example = "EXPENSE-PROMO-001")
            @PathVariable String ruleId) {
        // TODO: 实现规则统计信息查询
        return ResponseEntity.ok().build();
    }
} 