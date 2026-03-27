import React, { useState } from 'react';
import { Highlight, themes } from "prism-react-renderer";

// --- Inline Icons (No 'lucide-react' dependency needed) ---
const CheckIcon = ({ className }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14" height="14" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round"
        className={className}
    >
        <polyline points="20 6 9 17 4 12" />
    </svg>
);

const CopyIcon = ({ className }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14" height="14" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round"
        className={className}
    >
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
);

/**
 * A reusable Code Header component for Docusaurus.
 * Integrates Prism React Renderer for syntax highlighting.
 */
const CodeHeader = ({ title = "Code", children }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        if (typeof navigator !== 'undefined' && navigator.clipboard) {
            try {
                const textToCopy = typeof children === 'string' ? children : String(children);
                await navigator.clipboard.writeText(textToCopy);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            } catch (err) {
                console.error('Failed to copy code:', err);
            }
        }
    };

    // Map colloquial titles to Prism languages
    const getLanguage = (t) => {
        const lower = t.toLowerCase();
        if (lower.includes('react') || lower.includes('vue') || lower.includes('js')) return 'javascript';
        if (lower.includes('ts') || lower.includes('angular')) return 'typescript';
        if (lower.includes('bash') || lower === 'sh') return 'bash';
        if (lower === 'json') return 'json';
        if (lower.includes('python')) return 'python';
        return 'javascript'; // default
    };

    // --- High Specificity Styles to Override Infima ---
    const containerStyle = {
        width: '100%',
        margin: '1rem 0',
        borderRadius: '12px',
        overflow: 'hidden',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        backgroundColor: '#1e1e1e',
        border: '1px solid #3f3f46', // zinc-700
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
        fontSize: '0.875rem'
    };

    const headerStyle = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.625rem 1rem',
        backgroundColor: '#27272a', // zinc-800
        borderBottom: '1px solid #3f3f46', // zinc-700
        userSelect: 'none'
    };

    const titleStyle = {
        fontSize: '0.75rem',
        fontWeight: 'bold',
        color: '#e4e4e7', // zinc-200
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
    };

    const buttonStyle = {
        padding: '0.375rem',
        borderRadius: '0.25rem',
        backgroundColor: 'transparent',
        border: 'none',
        cursor: 'pointer',
        color: '#9ca3af', // gray-400
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    };

    return (
        <div style={containerStyle} className="group">
            {/* Header Bar */}
            <div style={headerStyle}>
                <span style={titleStyle}>
                    {/* Window Controls */}
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444', display: 'inline-block', opacity: 0.8 }}></span>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#eab308', display: 'inline-block', opacity: 0.8 }}></span>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#22c55e', display: 'inline-block', opacity: 0.8 }}></span>
                    <span style={{ marginLeft: '8px', opacity: 0.9 }}>{title}</span>
                </span>
                <button
                    onClick={handleCopy}
                    style={buttonStyle}
                    title="Copy code"
                    type="button"
                    onMouseEnter={(e) => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = '#9ca3af'; e.currentTarget.style.backgroundColor = 'transparent'; }}
                >
                    {copied ? <CheckIcon className="text-emerald-400" /> : <CopyIcon />}
                </button>
            </div>

            {/* Code Content Area */}
            <div style={{ overflowX: 'auto', backgroundColor: '#1e1e1e', padding: 0, margin: 0 }}>
                <Highlight
                    theme={themes.vsDark}
                    code={typeof children === 'string' ? children.trim() : String(children).trim()}
                    language={getLanguage(title)}
                >
                    {({ className, style, tokens, getLineProps, getTokenProps }) => (
                        <pre style={{
                            ...style,
                            backgroundColor: 'transparent',
                            padding: '1.25rem',
                            margin: 0,
                            fontFamily: 'inherit',
                            fontSize: '13px',
                            lineHeight: '1.5',
                            float: 'left',
                            minWidth: '100%'
                        }}>
                            {tokens.map((line, i) => (
                                <div key={i} {...getLineProps({ line })}>
                                    {line.map((token, key) => (
                                        <span key={key} {...getTokenProps({ token })} />
                                    ))}
                                </div>
                            ))}
                        </pre>
                    )}
                </Highlight>
            </div>
        </div>
    );
};

export default CodeHeader;