import React from 'react';

export default function Toast({ message }) {
  return (
    <div
      style={{
        position: 'fixed',
        top: 24,
        right: 32,
        background: 'linear-gradient(90deg,#43e97b 0%,#38f9d7 100%)',
        color: '#222',
        padding: '12px 28px',
        borderRadius: 22,
        fontWeight: 600,
        fontSize: 16,
        boxShadow: '0 4px 16px rgba(56, 249, 215, 0.13)',
        zIndex: 100,
        minWidth: 120,
        maxWidth: 320,
        textAlign: 'center',
        letterSpacing: 0.1,
        opacity: 0.97,
        animation: 'fadeIn 0.5s',
      }}
    >
      {message}
    </div>
  );
}
