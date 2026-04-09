#!/bin/bash
# Installs git hooks for the project

HOOKS_DIR=".git/hooks"
PRE_PUSH_HOOK="$HOOKS_DIR/pre-push"

echo "Installing pre-push hook..."

cat << 'HOOK_EOF' > "$PRE_PUSH_HOOK"
#!/bin/bash
# Pre-push hook to audit documentation traceability

echo "Running Documentation Audit (src/scripts/audit_docs.py)..."
python3 src/scripts/audit_docs.py

if [ $? -ne 0 ]; then
    echo "❌ Push aborted due to documentation audit failure."
    echo "Please ensure all Python files have an @Architecture-Map anchor and are documented in docs/reference/07_ARCHITECTURE_MAP.md."
    exit 1
fi

echo "✅ Documentation Audit passed."
exit 0
HOOK_EOF

chmod +x "$PRE_PUSH_HOOK"

echo "✅ pre-push hook installed successfully at $PRE_PUSH_HOOK."
