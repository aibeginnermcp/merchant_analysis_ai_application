package com.guardian.audit;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.scheduling.annotation.EnableScheduling;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.info.Contact;

/**
 * 审计服务启动类
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
@EnableScheduling
@OpenAPIDefinition(
    info = @Info(
        title = "审计规则引擎服务 API",
        version = "1.0.0",
        description = "提供规则管理、规则执行和审计结果查询等功能",
        contact = @Contact(
            name = "Financial Guardian Team",
            email = "support@guardian.com",
            url = "https://www.guardian.com"
        )
    )
)
public class AuditServiceApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(AuditServiceApplication.class, args);
    }
} 