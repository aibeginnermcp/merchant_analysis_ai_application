package com.guardian.audit.service;

import com.guardian.audit.model.*;
import com.guardian.audit.exception.RuleEngineException;
import org.drools.core.impl.InternalKnowledgeBase;
import org.kie.api.KieServices;
import org.kie.api.builder.KieBuilder;
import org.kie.api.builder.KieFileSystem;
import org.kie.api.builder.Message;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.yaml.snakeyaml.Yaml;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.*;

/**
 * 规则引擎核心服务类
 * 负责规则的加载、编译和执行
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
@Service
public class RuleEngineService {
    private static final Logger logger = LoggerFactory.getLogger(RuleEngineService.class);
    
    private final KieServices kieServices;
    private KieContainer kieContainer;
    private final Map<String, AuditRule> ruleRegistry;

    public RuleEngineService() {
        this.kieServices = KieServices.Factory.get();
        this.ruleRegistry = new HashMap<>();
        initializeRuleEngine();
    }

    /**
     * 初始化规则引擎
     * 加载规则模板并编译为可执行规则
     */
    private void initializeRuleEngine() {
        try {
            // 加载规则模板
            loadRuleTemplates();
            
            // 编译规则
            compileRules();
            
            logger.info("规则引擎初始化完成，共加载 {} 条规则", ruleRegistry.size());
        } catch (Exception e) {
            logger.error("规则引擎初始化失败", e);
            throw new RuleEngineException("规则引擎初始化失败", e);
        }
    }

    /**
     * 加载规则模板
     * 从audit_rules/templates目录下加载所有规则文件
     */
    private void loadRuleTemplates() throws IOException {
        File templateDir = new File("audit_rules/templates");
        if (!templateDir.exists()) {
            throw new RuleEngineException("规则模板目录不存在");
        }

        Yaml yaml = new Yaml();
        for (File file : templateDir.listFiles((dir, name) -> name.endsWith(".yaml"))) {
            try (FileInputStream input = new FileInputStream(file)) {
                Map<String, Object> ruleSet = yaml.load(input);
                processRuleSet(ruleSet);
            }
        }
    }

    /**
     * 处理规则集合
     * 将YAML格式的规则转换为内部规则对象
     */
    @SuppressWarnings("unchecked")
    private void processRuleSet(Map<String, Object> ruleSet) {
        Map<String, Map<String, Object>> rules = (Map<String, Map<String, Object>>) ruleSet.get("rules");
        for (Map.Entry<String, Map<String, Object>> entry : rules.entrySet()) {
            String ruleId = entry.getKey();
            Map<String, Object> ruleData = entry.getValue();
            
            AuditRule rule = AuditRule.builder()
                .id(ruleId)
                .name((String) ruleData.get("name"))
                .description((String) ruleData.get("description"))
                .condition((String) ruleData.get("condition"))
                .severity(RuleSeverity.valueOf((String) ruleData.get("severity")))
                .actions((List<String>) ruleData.get("action"))
                .references((List<String>) ruleData.get("references"))
                .build();
                
            ruleRegistry.put(ruleId, rule);
        }
    }

    /**
     * 编译规则
     * 将规则转换为Drools可执行的规则语言
     */
    private void compileRules() {
        KieFileSystem kfs = kieServices.newKieFileSystem();
        
        for (AuditRule rule : ruleRegistry.values()) {
            String drl = convertToDRL(rule);
            String path = "src/main/resources/rules/" + rule.getId() + ".drl";
            kfs.write(path, drl);
        }

        KieBuilder kieBuilder = kieServices.newKieBuilder(kfs);
        kieBuilder.buildAll();

        if (kieBuilder.getResults().hasMessages(Message.Level.ERROR)) {
            throw new RuleEngineException("规则编译失败: " + kieBuilder.getResults().toString());
        }

        kieContainer = kieServices.newKieContainer(kieServices.getRepository().getDefaultReleaseId());
    }

    /**
     * 将规则转换为Drools规则语言(DRL)格式
     */
    private String convertToDRL(AuditRule rule) {
        StringBuilder drl = new StringBuilder();
        
        // 包声明
        drl.append("package com.guardian.audit.rules;\n\n");
        
        // 导入语句
        drl.append("import com.guardian.audit.model.*;\n");
        drl.append("import java.util.*;\n\n");
        
        // 规则定义
        drl.append("rule \"").append(rule.getId()).append("\"\n");
        drl.append("    when\n");
        drl.append("        ").append(convertConditionToDRL(rule.getCondition())).append("\n");
        drl.append("    then\n");
        
        // 规则动作
        for (String action : rule.getActions()) {
            drl.append("        // ").append(action).append("\n");
        }
        
        drl.append("end\n");
        
        return drl.toString();
    }

    /**
     * 将规则条件转换为DRL格式
     */
    private String convertConditionToDRL(String condition) {
        // TODO: 实现复杂条件转换逻辑
        return condition;
    }

    /**
     * 执行规则检查
     * @param facts 待检查的事实数据
     * @return 检查结果列表
     */
    public List<AuditResult> executeRules(Collection<?> facts) {
        List<AuditResult> results = new ArrayList<>();
        KieSession kieSession = kieContainer.newKieSession();
        
        try {
            // 插入事实数据
            for (Object fact : facts) {
                kieSession.insert(fact);
            }
            
            // 设置全局变量
            kieSession.setGlobal("results", results);
            
            // 执行规则
            kieSession.fireAllRules();
            
        } finally {
            kieSession.dispose();
        }
        
        return results;
    }

    /**
     * 获取已加载的规则列表
     */
    public Collection<AuditRule> getAllRules() {
        return Collections.unmodifiableCollection(ruleRegistry.values());
    }

    /**
     * 根据ID获取规则
     */
    public Optional<AuditRule> getRuleById(String ruleId) {
        return Optional.ofNullable(ruleRegistry.get(ruleId));
    }
} 