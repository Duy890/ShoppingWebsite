-- Gaming capability benchmark tables.
-- Base.metadata.create_all() creates these tables automatically on startup.
-- Use this file for manual migration in existing database environments.

CREATE TABLE gpu_benchmarks (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  aliases TEXT,
  score INTEGER NOT NULL,
  created_at DATETIME
);

CREATE INDEX idx_gpu_benchmarks_name ON gpu_benchmarks(name);

CREATE TABLE cpu_benchmarks (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  aliases TEXT,
  score INTEGER NOT NULL,
  created_at DATETIME
);

CREATE INDEX idx_cpu_benchmarks_name ON cpu_benchmarks(name);

CREATE TABLE game_requirements (
  id VARCHAR(36) PRIMARY KEY,
  game_name VARCHAR(255) NOT NULL UNIQUE,
  aliases TEXT,
  min_gpu_score INTEGER NOT NULL,
  recommended_gpu_score INTEGER NOT NULL,
  ultra_gpu_score INTEGER NOT NULL,
  min_cpu_score INTEGER NOT NULL,
  recommended_cpu_score INTEGER NOT NULL,
  ultra_cpu_score INTEGER NOT NULL,
  min_ram_gb INTEGER NOT NULL,
  recommended_ram_gb INTEGER NOT NULL,
  ultra_ram_gb INTEGER NOT NULL,
  created_at DATETIME
);

CREATE INDEX idx_game_requirements_game_name ON game_requirements(game_name);
