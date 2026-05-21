CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS usuarios (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    nome        VARCHAR(100) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS animais (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    especie     VARCHAR(50) NOT NULL,
    raca        VARCHAR(100),
    idade       INTEGER,
    peso        DECIMAL(5,2),
    nome_dono   VARCHAR(100) NOT NULL,
    contato_dono VARCHAR(20),
    foto_url    TEXT,
    observacoes TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consultas (
    id              SERIAL PRIMARY KEY,
    animal_id       INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    data_consulta   TIMESTAMP NOT NULL,
    veterinario     VARCHAR(100) NOT NULL,
    motivo          TEXT NOT NULL,
    diagnostico     TEXT,
    tratamento      TEXT,
    medicamentos    TEXT,
    peso_consulta   DECIMAL(5,2),
    retorno         DATE,
    status          VARCHAR(20) DEFAULT 'agendada' CHECK (status IN ('agendada', 'realizada', 'cancelada')),
    observacoes     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_animais_nome ON animais(nome);
CREATE INDEX IF NOT EXISTS idx_animais_especie ON animais(especie);
CREATE INDEX IF NOT EXISTS idx_consultas_animal ON consultas(animal_id);
CREATE INDEX IF NOT EXISTS idx_consultas_data ON consultas(data_consulta);
CREATE INDEX IF NOT EXISTS idx_consultas_status ON consultas(status);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_animais_updated_at
    BEFORE UPDATE ON animais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consultas_updated_at
    BEFORE UPDATE ON consultas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO animais (nome, especie, raca, idade, peso, nome_dono, contato_dono, observacoes) VALUES
    ('Rex', 'Cachorro', 'Labrador', 3, 28.5, 'João Silva', '(47) 99999-1111', 'Animal dócil e vacinado em dia'),
    ('Mimi', 'Gato', 'Siamês', 5, 4.2, 'Maria Santos', '(47) 98888-2222', 'Alergia a determinados alimentos'),
    ('Pingo', 'Cachorro', 'Poodle', 2, 6.8, 'Carlos Oliveira', '(47) 97777-3333', NULL),
    ('Luna', 'Gato', 'Persa', 4, 5.1, 'Ana Costa', '(47) 96666-4444', 'Castrada'),
    ('Bolt', 'Cachorro', 'Border Collie', 1, 15.3, 'Pedro Lima', '(47) 95555-5555', 'Muito ativo, precisa de exercícios');

INSERT INTO consultas (animal_id, data_consulta, veterinario, motivo, diagnostico, tratamento, status) VALUES
    (1, NOW() - INTERVAL '30 days', 'Dr. Carlos Mendes', 'Consulta de rotina', 'Animal saudável', 'Nenhum tratamento necessário', 'realizada'),
    (2, NOW() - INTERVAL '15 days', 'Dra. Ana Ferreira', 'Vômitos frequentes', 'Gastrite leve', 'Dieta branda por 5 dias + omeprazol', 'realizada'),
    (3, NOW() + INTERVAL '2 days', 'Dr. Carlos Mendes', 'Vacinação anual', NULL, NULL, 'agendada'),
    (1, NOW() + INTERVAL '7 days', 'Dra. Ana Ferreira', 'Retorno pós-cirurgia', NULL, NULL, 'agendada'),
    (4, NOW() - INTERVAL '5 days', 'Dr. Carlos Mendes', 'Queda de pelos', 'Dermatite alérgica', 'Shampoo medicinal + anti-histamínico', 'realizada');

DO $$
BEGIN
    RAISE NOTICE 'Banco de dados da Clínica Veterinária inicializado com sucesso!';
END $$;