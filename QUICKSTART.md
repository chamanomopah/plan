# 🚀 Quick Start: Testar o Workflow Automatizado

## 📦 O Que Foi Criado

Sistema de **4 hooks automatizados** que implementam um workflow contínuo:
- **TEST** → **REVIEW** → **PATCH** → **IMPLEMENT** → (loop)

## 🎯 Teste Rápido (5 minutos)

### 1️⃣ Dar Permissão aos Scripts

```bash
chmod +x .claude/hooks/*.sh
```

### 2️⃣ Iniciar o Claude

```bash
claude
```

### 3️⃣ Implementar o Spec de Exemplo

```
/implement specs/example-calculator-api.md
```

### 4️⃣ Esperar a Implementação

O Claude vai criar:
- `server.js` - Servidor Express
- `calculator.js` - Lógica da calculadora
- `package.json` - Dependências
- `tests/calculator.test.js` - Testes

### 5️⃣ Sair e Ver o Mágica

```
/exit
```

**Boom!** O workflow automático inicia:
1. ✅ Roda os testes
2. ✅ Review a implementação
3. ✅ Cria patches se necessário
4. ✅ Implementa as correções
5. ✅ Repete até tudo passar

## 📊 Acompanhar a Execução

```bash
# Ver logs em tempo real (outro terminal)
tail -f .claude/workflow/workflow.log

# Ver estado
cat .claude/workflow/state.json | jq

# Ver resultados
cat .claude/workflow/last-test-output.json | jq
cat .claude/workflow/last-review-output.json | jq
```

## 📚 Documentação Completa

- **[specs/test-example-calculator.md](specs/test-example-calculator.md)** - Guia detalhado do teste
- **[.claude/SUMMARY.md](.claude/SUMMARY.md)** - Resumo do sistema
- **[.claude/hooks/README.md](.claude/hooks/README.md)** - Documentação dos hooks
- **[.claude/docs/05-workflow-hooks.md](.claude/docs/05-workflow-hooks.md)** - Docs técnicas

## 🎯 Resultados Esperados

### Sucesso Total
```
✅ All tests passed
✅ Review passed - no blockers
🎉 Workflow completed successfully!
```

### Com Issues (Automaticamente Corrigido)
```
⚠️ Found blockers
🩹 Creating patch...
🔨 Implementing patch...
🔄 Testing again...
✅ All blockers resolved!
```

## 🔧 Troubleshooting

**Workflow não inicia?**
```bash
chmod +x .claude/hooks/*.sh
```

**Ver detalhes:**
```bash
claude --debug
tail -f .claude/workflow/workflow.log
```

## ✅ Pronto!

Agora você tem um sistema automatizado que:
- Valida implementações
- Encontra issues automaticamente
- Cria correções cirúrgicas
- Itera até o sucesso

**Use specs próprios para testar com seus projetos!**
