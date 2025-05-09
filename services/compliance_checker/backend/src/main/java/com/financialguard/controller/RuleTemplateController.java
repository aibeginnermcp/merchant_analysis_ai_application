package com.financialguard.controller;

import com.financialguard.model.RuleTemplate;
import com.financialguard.service.RuleTemplateService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 规则模板控制器
 * 提供规则模板管理的REST API
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Tag(name = "规则模板管理", description = "提供规则模板的增删改查等管理功能")
@RestController
@RequestMapping("/api/v1/templates")
@Validated
public class RuleTemplateController {

    private final RuleTemplateService templateService;

    @Autowired
    public RuleTemplateController(RuleTemplateService templateService) {
        this.templateService = templateService;
    }

    /**
     * 创建规则模板
     */
    @Operation(summary = "创建规则模板", description = "创建新的规则模板")
    @PostMapping
    public ResponseEntity<RuleTemplate> createTemplate(
            @RequestBody @Validated RuleTemplate template) {
        return ResponseEntity.ok(templateService.createTemplate(template));
    }

    /**
     * 更新规则模板
     */
    @Operation(summary = "更新规则模板", description = "更新现有的规则模板")
    @PutMapping("/{code}")
    public ResponseEntity<RuleTemplate> updateTemplate(
            @Parameter(description = "模板编码") @PathVariable String code,
            @RequestBody @Validated RuleTemplate template) {
        template.setCode(code);
        return ResponseEntity.ok(templateService.updateTemplate(template));
    }

    /**
     * 获取规则模板
     */
    @Operation(summary = "获取规则模板", description = "根据编码获取规则模板")
    @GetMapping("/{code}")
    public ResponseEntity<RuleTemplate> getTemplate(
            @Parameter(description = "模板编码") @PathVariable String code) {
        return templateService.findByCode(code)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * 获取所有启用的模板
     */
    @Operation(summary = "获取所有启用的模板", description = "获取系统中所有启用状态的规则模板")
    @GetMapping
    public ResponseEntity<List<RuleTemplate>> getAllEnabledTemplates() {
        return ResponseEntity.ok(templateService.findAllEnabled());
    }

    /**
     * 根据类型获取模板
     */
    @Operation(summary = "获取指定类型的模板", description = "获取指定类型的规则模板")
    @GetMapping("/type/{type}")
    public ResponseEntity<List<RuleTemplate>> getTemplatesByType(
            @Parameter(description = "模板类型") @PathVariable String type) {
        return ResponseEntity.ok(templateService.findByType(type));
    }

    /**
     * 启用模板
     */
    @Operation(summary = "启用模板", description = "启用指定的规则模板")
    @PostMapping("/{code}/enable")
    public ResponseEntity<Void> enableTemplate(
            @Parameter(description = "模板编码") @PathVariable String code) {
        templateService.enableTemplate(code);
        return ResponseEntity.ok().build();
    }

    /**
     * 禁用模板
     */
    @Operation(summary = "禁用模板", description = "禁用指定的规则模板")
    @PostMapping("/{code}/disable")
    public ResponseEntity<Void> disableTemplate(
            @Parameter(description = "模板编码") @PathVariable String code) {
        templateService.disableTemplate(code);
        return ResponseEntity.ok().build();
    }

    /**
     * 根据模板生成规则
     */
    @Operation(summary = "生成规则", description = "根据模板和参数生成规则")
    @PostMapping("/{code}/generate")
    public ResponseEntity<String> generateRule(
            @Parameter(description = "模板编码") @PathVariable String code,
            @RequestBody Map<String, Object> parameters) {
        return ResponseEntity.ok(templateService.generateRule(code, parameters));
    }
} 