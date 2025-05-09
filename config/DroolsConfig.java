package com.financialguard.config;

import org.kie.api.KieServices;
import org.kie.api.builder.*;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;
import org.kie.internal.io.ResourceFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Drools规则引擎配置类
 * 负责初始化规则引擎环境和管理规则会话
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Configuration
public class DroolsConfig {

    private final KieServices kieServices = KieServices.Factory.get();

    /**
     * 创建规则容器
     * 
     * @return KieContainer实例
     * @throws Exception 规则加载异常
     */
    @Bean
    public KieContainer kieContainer() throws Exception {
        KieFileSystem kieFileSystem = kieServices.newKieFileSystem();
        
        // 加载默认规则文件
        loadDefaultRules(kieFileSystem);
        
        KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
        kieBuilder.buildAll();
        
        Results results = kieBuilder.getResults();
        if (results.hasMessages(Message.Level.ERROR)) {
            throw new Exception("规则文件编译错误: " + results.getMessages());
        }
        
        return kieServices.newKieContainer(kieServices.getRepository()
                .getDefaultReleaseId());
    }

    /**
     * 创建规则会话
     * 
     * @param kieContainer 规则容器
     * @return KieSession实例
     */
    @Bean
    public KieSession kieSession(KieContainer kieContainer) {
        return kieContainer.newKieSession();
    }

    /**
     * 加载默认规则文件
     * 
     * @param kieFileSystem 规则文件系统
     */
    private void loadDefaultRules(KieFileSystem kieFileSystem) {
        // 加载促销费用规则
        String promotionRule = "package com.financialguard.rules;\n" +
                "import com.financialguard.model.*;\n" +
                "rule \"促销费用超限检查\"\n" +
                "when\n" +
                "    $expense : ExpenseData(type == \"促销费用\", " +
                "amount / gmv > 0.05, explanation == null)\n" +
                "then\n" +
                "    insert(new AuditAlert(RuleSeverity.HIGH, " +
                "\"促销费用占比超过5%且无说明\"));\n" +
                "end";
        
        kieFileSystem.write("src/main/resources/rules/promotion.drl", 
                ResourceFactory.newByteArrayResource(promotionRule.getBytes()));
                
        // TODO: 加载更多默认规则
    }
} 