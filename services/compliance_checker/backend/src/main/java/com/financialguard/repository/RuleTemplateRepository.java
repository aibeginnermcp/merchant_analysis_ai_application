package com.financialguard.repository;

import com.financialguard.model.RuleTemplate;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 规则模板数据访问接口
 * 
 * @author FinancialGuard
 * @version 1.0
 * @since 2024-03-20
 */
@Repository
public interface RuleTemplateRepository extends JpaRepository<RuleTemplate, Long> {
    
    /**
     * 根据模板编码查找模板
     * 
     * @param code 模板编码
     * @return 模板对象
     */
    Optional<RuleTemplate> findByCode(String code);

    /**
     * 查找所有启用的模板
     * 
     * @return 模板列表
     */
    List<RuleTemplate> findByEnabledTrue();

    /**
     * 根据类型查找模板
     * 
     * @param type 模板类型
     * @return 模板列表
     */
    List<RuleTemplate> findByType(String type);

    /**
     * 根据会计准则查找模板
     * 
     * @param standard 会计准则
     * @return 模板列表
     */
    List<RuleTemplate> findByAccountingStandard(String standard);

    /**
     * 检查模板编码是否已存在
     * 
     * @param code 模板编码
     * @return 是否存在
     */
    boolean existsByCode(String code);
} 