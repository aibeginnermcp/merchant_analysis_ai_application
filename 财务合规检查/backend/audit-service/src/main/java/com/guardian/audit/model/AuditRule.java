package com.guardian.audit.model;

import lombok.Builder;
import lombok.Data;
import java.util.List;

/**
 * 审计规则模型类
 * 用于表示一条完整的审计规则定义
 * 
 * @author Financial Guardian Team
 * @version 1.0.0
 */
@Data
@Builder
public class AuditRule {
    /**
     * 规则唯一标识
     * 格式：{模块}-{类型}-{序号}
     * 示例：EXPENSE-PROMO-001
     */
    private String id;
    
    /**
     * 规则名称
     * 简短描述规则的主要功能
     */
    private String name;
    
    /**
     * 规则描述
     * 详细说明规则的检查内容和目的
     */
    private String description;
    
    /**
     * 规则条件
     * 使用DSL语法描述的规则触发条件
     */
    private String condition;
    
    /**
     * 规则严重程度
     * 用于标识规则违反的严重程度
     */
    private RuleSeverity severity;
    
    /**
     * 规则动作
     * 当规则条件满足时需要执行的动作列表
     */
    private List<String> actions;
    
    /**
     * 规则依据
     * 相关的法律法规、会计准则等参考依据
     */
    private List<String> references;
    
    /**
     * 规则状态
     * 标识规则是否启用
     */
    private boolean enabled;
    
    /**
     * 规则版本
     * 用于版本控制和追踪
     */
    private String version;
    
    /**
     * 最后修改时间
     * 记录规则的最后更新时间
     */
    private long lastModified;
    
    /**
     * 修改人
     * 记录最后修改规则的人员
     */
    private String modifiedBy;
} 