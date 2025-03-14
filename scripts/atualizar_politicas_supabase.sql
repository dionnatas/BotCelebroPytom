-- Remover políticas existentes (se houver)
DROP POLICY IF EXISTS "Permitir acesso para todos" ON ideias;
DROP POLICY IF EXISTS "Permitir acesso para todos" ON brainstorms;

-- Criar políticas que permitem acesso total a todos os usuários
CREATE POLICY "Permitir acesso para todos" ON ideias
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Permitir acesso para todos" ON brainstorms
  USING (true)
  WITH CHECK (true);

-- Garantir que o RLS está habilitado (necessário para que as políticas funcionem)
ALTER TABLE ideias ENABLE ROW LEVEL SECURITY;
ALTER TABLE brainstorms ENABLE ROW LEVEL SECURITY;
