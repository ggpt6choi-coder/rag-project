import React, { useState, useRef, useEffect } from 'react';
import useChatStorage from '../hooks/useChatStorage';

export default function ChatPanel({ collectionName }) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useChatStorage(collectionName);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !collectionName) return;
    const now = new Date();
    const userMsg = {
      role: 'user',
      content: input,
      timestamp: now.toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);
    setInput('');

    // AbortController 생성 및 저장
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const res = await fetch('/api/v1/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          collection_name: collectionName,
          history: messages,
        }),
        signal: controller.signal,
      });
      const data = await res.json();
      const now2 = new Date();
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer || data.message,
          timestamp: now2.toISOString(),
        },
      ]);
    } catch (err) {
      if (err.name === 'AbortError') {
        // 취소 시 말풍선은 handleCancel에서 처리, 에러 메시지 없음
      } else {
        setError('답변 실패');
      }
    }
    setLoading(false);
    abortControllerRef.current = null;
  };

  // 답변 생성 취소 핸들러
  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setLoading(false);
      // 답변 말풍선에 취소 메시지 추가
      const now = new Date();
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '답변이 취소되었습니다.',
          timestamp: now.toISOString(),
        },
      ]);
      setError(null);
    }
  };

  // 부서가 바뀔 때마다 입력창 초기화
  useEffect(() => {
    setInput('');
  }, [collectionName]);

  const formatKoreanDateTime = (isoString) => {
    if (!isoString) return '';
    const d = new Date(isoString);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const hh = String(d.getHours()).padStart(2, '0');
    const min = String(d.getMinutes()).padStart(2, '0');
    const ss = String(d.getSeconds()).padStart(2, '0');
    return `${yyyy}.${mm}.${dd} ${hh}:${min}:${ss}`;
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: 'linear-gradient(180deg,#f7f8fa 60%,#e3e7ef 100%)',
        minHeight: 0,
      }}
    >
      {/* 메시지 영역 */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '68px 0 28px 0', // 상단 패딩을 68px로 늘림
          display: 'flex',
          flexDirection: 'column',
          gap: 22,
          minHeight: 0,
          minWidth: 0,
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              alignItems: 'flex-start',
              width: '100%',
              gap: 8,
            }}
          >
            {/* 말풍선 */}
            <div
              style={{
                maxWidth: '62%',
                background:
                  msg.role === 'user'
                    ? 'linear-gradient(90deg,#1976d2 60%,#42a5f5 100%)'
                    : '#fff',
                color: msg.role === 'user' ? '#fff' : '#23272f',
                borderRadius:
                  msg.role === 'user'
                    ? '22px 22px 6px 22px'
                    : '22px 22px 22px 6px',
                padding: '16px 22px',
                margin:
                  msg.role === 'user' ? '0 28px 0 0' : '0 0 0 28px',
                boxShadow: '0 4px 16px rgba(25, 118, 210, 0.10)',
                fontSize: 17,
                wordBreak: 'break-word',
                lineHeight: 1.8,
                border:
                  msg.role === 'user'
                    ? 'none'
                    : '1.5px solid #e0e0e0',
                position: 'relative',
                fontWeight: 500,
                letterSpacing: 0.1,
                marginBottom: 6,
              }}
            >
              {msg.role === 'assistant' && (
                <span
                  style={{
                    position: 'absolute',
                    left: -28,
                    top: 4,
                    fontSize: 24,
                    opacity: 0.7,
                  }}
                >
                  🤖
                </span>
              )}
              {msg.content}
            </div>
            {/* 복사 버튼 (말풍선 바깥) */}
            <div style={{ display: 'flex', alignItems: 'flex-start', height: '100%', marginTop: 2 }}>
              <div style={{ position: 'relative' }}>
                <button
                  onClick={e => {
                    navigator.clipboard.writeText(msg.content);
                    // scale 애니메이션
                    const btn = e.currentTarget;
                    if (btn) {
                      btn.style.transform = 'scale(1.25)';
                      setTimeout(() => {
                        if (btn) btn.style.transform = 'scale(1)';
                      }, 120);
                    }
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: 0,
                    margin: 0,
                    cursor: 'pointer',
                    opacity: 0.5,
                    fontSize: 17,
                    transition: 'opacity 0.15s, transform 0.13s cubic-bezier(.4,1.6,.6,1)',
                  }}
                  onMouseOver={e => {
                    e.currentTarget.style.opacity = 0.9;
                    const tooltip = e.currentTarget.nextSibling;
                    if (tooltip) tooltip.style.opacity = 1;
                  }}
                  onMouseOut={e => {
                    e.currentTarget.style.opacity = 0.5;
                    const tooltip = e.currentTarget.nextSibling;
                    if (tooltip) tooltip.style.opacity = 0;
                  }}
                  aria-label="복사"
                >
                  <span role="img" aria-label="복사">📋</span>
                </button>
                {/* 툴팁 */}
                <span
                  style={{
                    position: 'absolute',
                    left: '50%',
                    top: -28,
                    transform: 'translateX(-50%)',
                    background: '#23272f',
                    color: '#fff',
                    fontSize: 12,
                    padding: '3px 10px',
                    borderRadius: 8,
                    whiteSpace: 'nowrap',
                    opacity: 0,
                    pointerEvents: 'none',
                    transition: 'opacity 0.15s',
                    zIndex: 10,
                  }}
                >복사</span>
              </div>
            </div>
            <div
              style={{
                fontSize: 13,
                color: '#bdbdbd',
                marginTop: 2,
                marginLeft: msg.role === 'user' ? 'auto' : 28,
                marginRight: msg.role === 'user' ? 28 : 'auto',
                textAlign: msg.role === 'user' ? 'right' : 'left',
                maxWidth: '62%',
              }}
            >
              {msg.timestamp ? formatKoreanDateTime(msg.timestamp) : ''}
            </div>
          </div>
        ))
        }
        {
          loading && (
            <div
              style={{
                display: 'flex',
                justifyContent: 'flex-start',
                width: '100%',
              }}
            >
              <div
                style={{
                  maxWidth: '62%',
                  background: '#fff',
                  color: '#23272f',
                  borderRadius: '22px 22px 22px 6px',
                  padding: '16px 22px',
                  margin: '0 0 0 28px',
                  boxShadow: '0 4px 16px rgba(25, 118, 210, 0.10)',
                  fontSize: 17,
                  fontWeight: 500,
                  letterSpacing: 0.1,
                  border: '1.5px solid #e0e0e0',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}
              >
                <span style={{ fontSize: 22, opacity: 0.7 }}>🤖</span>
                <span>답변 생성 중...</span>
                <span
                  className="loader"
                  style={{
                    marginLeft: 8,
                    width: 16,
                    height: 16,
                    border: '2px solid #bdbdbd',
                    borderTop: '2px solid #1976d2',
                    borderRadius: '50%',
                    display: 'inline-block',
                    animation: 'spin 1s linear infinite',
                  }}
                />
                <button
                  onClick={handleCancel}
                  style={{
                    marginLeft: 12,
                    fontSize: 13,
                    color: '#1976d2',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 0,
                    fontWeight: 600,
                    opacity: 0.8,
                  }}
                >
                  취소
                </button>
              </div>
            </div>
          )
        }
        <div ref={messagesEndRef} />
      </div >

      {/* 입력창 */}
      < form
        style={{
          display: 'flex',
          alignItems: 'center',
          padding: '20px 36px',
          background: '#f7f7fa',
          borderTop: '1.5px solid #e0e0e0',
          boxShadow: '0 -2px 12px rgba(0,0,0,0.03)',
          minWidth: 0,
        }}
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          style={{
            flex: 1,
            border: 'none',
            borderRadius: 28,
            padding: '16px 22px',
            fontSize: 17,
            background: '#fff',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            outline: 'none',
            marginRight: 14,
            fontWeight: 500,
            letterSpacing: 0.1,
          }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            collectionName
              ? '메시지를 입력하세요...'
              : '부서를 먼저 선택하세요'
          }
          disabled={!collectionName || loading}
        />
        <button
          type="submit"
          style={{
            background: 'linear-gradient(90deg,#1976d2 60%,#42a5f5 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: 28,
            padding: '13px 32px',
            fontWeight: 700,
            fontSize: 17,
            cursor:
              !input.trim() || !collectionName || loading
                ? 'not-allowed'
                : 'pointer',
            opacity:
              !input.trim() || !collectionName || loading ? 0.5 : 1,
            transition: 'all 0.18s',
            boxShadow: '0 2px 8px rgba(25, 118, 210, 0.10)',
            letterSpacing: 0.1,
          }}
          disabled={!input.trim() || !collectionName || loading}
        >
          전송
        </button>
      </form >
      {error && (
        <div
          style={{
            color: '#d32f2f',
            fontSize: 15,
            padding: 10,
            textAlign: 'center',
            fontWeight: 500,
          }}
        >
          {error}
        </div>
      )}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div >
  );
}
