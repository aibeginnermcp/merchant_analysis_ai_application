// 为高频查询字段建立索引，提升查询性能
// 现金流分析相关
// analysis_collection: merchant_id + time_range.start_date + time_range.end_date
// prediction_collection: merchant_id, created_at, metadata.prediction_id
// costs_collection: merchant_id, timestamp
// merchants_collection: merchant_id
// documents_collection: merchant_id, document_id
// check_results_collection: merchant_id, check_id, check_date
// violations_collection: check_id

/**
 * 初始化高频查询字段索引
 * 使用方法：
 *   mongo mongodb://localhost:27017/merchant_analytics create_indexes.js
 */
db = db.getSiblingDB('merchant_analytics');

// 现金流分析
if (db.analysis_collection) {
  db.analysis_collection.createIndex({merchant_id: 1, "time_range.start_date": 1, "time_range.end_date": 1});
}
if (db.prediction_collection) {
  db.prediction_collection.createIndex({merchant_id: 1, created_at: -1});
  db.prediction_collection.createIndex({"metadata.prediction_id": 1});
}

// 成本分析
if (db.costs_collection) {
  db.costs_collection.createIndex({merchant_id: 1, timestamp: 1});
}
if (db.merchants_collection) {
  db.merchants_collection.createIndex({merchant_id: 1});
}

// 合规检查
if (db.documents_collection) {
  db.documents_collection.createIndex({merchant_id: 1});
  db.documents_collection.createIndex({document_id: 1});
}
if (db.check_results_collection) {
  db.check_results_collection.createIndex({merchant_id: 1, check_date: -1});
  db.check_results_collection.createIndex({check_id: 1});
}
if (db.violations_collection) {
  db.violations_collection.createIndex({check_id: 1});
} 