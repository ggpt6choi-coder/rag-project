// 파일 전체를 App.jsx로 이동
import React, { useState } from 'react';
import DepartmentList from './components/DepartmentList';
import ChatPanel from './components/ChatPanel';
import FileUpload from './components/FileUpload';
import { QueryClient, QueryClientProvider } from 'react-query';
import Toast from './components/Toast';

const queryClient = new QueryClient();

export default function App() {
  const [selectedDept, setSelectedDept] = useState(null);
  const [toast, setToast] = useState(null);

  const handleDeptSelect = (dept) => setSelectedDept(dept);
  const handleUploadSuccess = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div
        style={{
          display: 'flex',
          height: '100vh',
          minHeight: 0,
          width: '100vw',
          overflow: 'hidden',
          background: '#ececf1',
        }}
      >
        {/* 좌측: chatGPT 스타일 사이드바 */}
        <aside
          style={{
            width: 260,
            minWidth: 120,
            maxWidth: 320,
            background: '#202123',
            color: '#fff',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '2px 0 8px rgba(0,0,0,0.04)',
            zIndex: 10,
            height: '100%',
            minHeight: 0,
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 22, padding: '28px 0 18px 32px', letterSpacing: 1, color: '#fff', borderBottom: '1px solid #2a2b32' }}>부서 선택</div>
          <DepartmentList selected={selectedDept} onSelect={handleDeptSelect} />
        </aside>
        {/* 우측: chatGPT 스타일 대화창 */}
        <main
          style={{
            flex: 1,
            minWidth: 0,
            display: 'flex',
            flexDirection: 'column',
            background: '#ececf1',
            height: '100%',
            minHeight: 0,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              height: 56,
              minHeight: 40,
              background: '#fff',
              borderBottom: '1px solid #e0e0e0',
              padding: '0 24px',
              boxShadow: '0 1px 4px rgba(0,0,0,0.03)',
              flexShrink: 0,
              gap: 10,
            }}
          >
            <FileUpload collectionName={selectedDept} onSuccess={handleUploadSuccess} disabled={!selectedDept} small />
            <button
              onClick={() => {
                if (window.confirm('정말 이 부서의 대화 기록을 모두 삭제할까요?')) {
                  localStorage.removeItem(selectedDept ? `chat_history_${selectedDept}` : '');
                  // ChatPanel이 messages를 새로 불러오도록 강제 트리거
                  window.dispatchEvent(new Event('storage'));
                }
              }}
              disabled={!selectedDept}
              style={{
                background: 'none',
                border: '1.5px solid #e0e0e0',
                color: '#888',
                borderRadius: 18,
                fontSize: 14,
                padding: '6px 18px',
                marginLeft: 2,
                fontWeight: 600,
                cursor: !selectedDept ? 'not-allowed' : 'pointer',
                opacity: !selectedDept ? 0.5 : 1,
                transition: 'all 0.18s',
                letterSpacing: 0.1,
              }}
              title="이 부서의 대화 기록 전체 삭제"
            >
              🗑 대화기록 삭제
            </button>
          </div>
          <div
            style={{
              flex: 1,
              minHeight: 0,
              minWidth: 0,
              display: 'flex',
              flexDirection: 'column',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <ChatPanel collectionName={selectedDept} />
          </div>
        </main>
        {toast && <Toast message={toast} />}
      </div>
    </QueryClientProvider>
  );
}
