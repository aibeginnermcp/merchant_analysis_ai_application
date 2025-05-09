package com.financialguard.engine;

import com.financialguard.model.AuditRule;
import org.kie.api.KieServices;
import org.kie.api.builder.*;
import org.kie.api.runtime.KieContainer;
import org.kie.internal.io.ResourceFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.Collection;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 规则加载器
 * 负责规则的动态加载和热更新
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Component
public class RuleLoader {
    
    private static final Logger logger = LoggerFactory.getLogger(RuleLoader.class);
    private final KieServices kieServices = KieServices.Factory.get();
    private final Map<String, String> ruleCache = new ConcurrentHashMap<>();
    private volatile KieContainer kieContainer;

    /**
     * 加载单个规则
     * 
     * @param rule 审计规则
     * @throws Exception 规则加载异常
     */
    public void loadRule(AuditRule rule) throws Exception {
        logger.info("开始加载规则: {}", rule.getCode());
        
        // 更新规则缓存
        ruleCache.put(rule.getCode(), rule.getContent());
        
        // 重新构建规则容器
        rebuildContainer();
        
        logger.info("规则加载完成: {}", rule.getCode());
    }

    /**
     * 批量加载规则
     * 
     * @param rules 规则集合
     * @throws Exception 规则加载异常
     */
    public void loadRules(Collection<AuditRule> rules) throws Exception {
        logger.info("开始批量加载规则，数量: {}", rules.size());
        
        // 更新规则缓存
        rules.forEach(rule -> ruleCache.put(rule.getCode(), rule.getContent()));
        
        // 重新构建规则容器
        rebuildContainer();
        
        logger.info("批量加载规则完成");
    }

    /**
     * 移除规则
     * 
     * @param ruleCode 规则编码
     * @throws Exception 规则移除异常
     */
    public void removeRule(String ruleCode) throws Exception {
        logger.info("开始移除规则: {}", ruleCode);
        
        // 从缓存中移除规则
        ruleCache.remove(ruleCode);
        
        // 重新构建规则容器
        rebuildContainer();
        
        logger.info("规则移除完成: {}", ruleCode);
    }

    /**
     * 重新构建规则容器
     * 
     * @throws Exception 构建异常
     */
    private synchronized void rebuildContainer() throws Exception {
        KieFileSystem kieFileSystem = kieServices.newKieFileSystem();
        
        // 将缓存中的所有规则添加到文件系统
        ruleCache.forEach((code, content) -> {
            String path = "src/main/resources/rules/" + code + ".drl";
            kieFileSystem.write(path, ResourceFactory.newByteArrayResource(content.getBytes()));
        });
        
        // 构建规则
        KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
        kieBuilder.buildAll();
        
        // 检查构建结果
        Results results = kieBuilder.getResults();
        if (results.hasMessages(Message.Level.ERROR)) {
            throw new Exception("规则构建错误: " + results.getMessages());
        }
        
        // 更新容器
        KieContainer newContainer = kieServices.newKieContainer(
                kieServices.getRepository().getDefaultReleaseId());
        
        // 原子性更新容器引用
        KieContainer oldContainer = this.kieContainer;
        this.kieContainer = newContainer;
        
        // 释放旧容器资源
        if (oldContainer != null) {
            oldContainer.dispose();
        }
    }

    /**
     * 获取规则容器
     * 
     * @return KieContainer实例
     */
    public KieContainer getKieContainer() {
        return kieContainer;
    }

    /**
     * 验证规则语法
     * 
     * @param ruleContent 规则内容
     * @return 是否有效
     */
    public boolean validateRule(String ruleContent) {
        try {
            KieFileSystem kieFileSystem = kieServices.newKieFileSystem();
            kieFileSystem.write("src/main/resources/rules/temp.drl",
                    ResourceFactory.newByteArrayResource(ruleContent.getBytes()));
            
            KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
            kieBuilder.buildAll();
            
            return !kieBuilder.getResults().hasMessages(Message.Level.ERROR);
        } catch (Exception e) {
            logger.error("规则验证失败: {}", e.getMessage());
            return false;
        }
    }
} 