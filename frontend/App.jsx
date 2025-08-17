// 파일 전체를 App.jsx로 이동
import React, { useState, useRef } from 'react';
import DepartmentList from './components/DepartmentList';
import ChatPanel from './components/ChatPanel';
import { QueryClient, QueryClientProvider } from 'react-query';
import Toast from './components/Toast';
import FileUpload from './components/FileUpload';

const queryClient = new QueryClient();



export default function App() {
  const [selectedDept, setSelectedDept] = useState(null);
  const [toast, setToast] = useState(null);
  const [unreadAnswers, setUnreadAnswers] = useState({}); // {부서명: true/false}
  const chatPanelRef = useRef();
  // 팀별 messages/loading 상태 관리
  const [chatStates, setChatStates] = useState({}); // { [부서명]: { messages: [], loading: false } }

  // 부서 클릭 시 해당 부서 unread 해제
  const handleDeptSelect = (dept) => {
    setSelectedDept(dept);
    setUnreadAnswers(prev => ({ ...prev, [dept]: false }));
  };

  const handleUploadSuccess = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  // 팀별 messages setter
  const setMessages = (dept, updater) => {
    setChatStates(prev => {
      const prevDeptState = prev[dept] || { messages: [], loading: false };
      const newMessages = typeof updater === 'function' ? updater(prevDeptState.messages) : updater;
      return { ...prev, [dept]: { ...prevDeptState, messages: newMessages } };
    });
  };
  // 팀별 loading setter
  const setLoading = (dept, value) => {
    setChatStates(prev => {
      const prevDeptState = prev[dept] || { messages: [], loading: false };
      return { ...prev, [dept]: { ...prevDeptState, loading: value } };
    });
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
          <DepartmentList selected={selectedDept} onSelect={handleDeptSelect} unreadAnswers={unreadAnswers} />
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
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ position: 'relative' }}>
                <button
                  onClick={() => {
                    if (window.confirm('정말 이 부서의 대화 기록을 모두 삭제할까요?')) {
                      localStorage.removeItem(selectedDept ? `chat_history_${selectedDept}` : '');
                      window.dispatchEvent(new Event('storage'));
                      if (chatPanelRef.current && chatPanelRef.current.clearMessages) {
                        chatPanelRef.current.clearMessages();
                      }
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
                  onMouseOver={e => e.currentTarget.style.background = '#f5f7fa'}
                  onMouseOut={e => e.currentTarget.style.background = 'none'}
                >
                  🗑 대화기록 삭제
                </button>
              </div>
              <div style={{ position: 'relative' }}>
                <FileUpload
                  collectionName={selectedDept}
                  onSuccess={handleUploadSuccess}
                  disabled={!selectedDept}
                  small
                  style={{
                    background: 'linear-gradient(90deg,#1976d2 60%,#42a5f5 100%)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 18,
                    fontSize: 14,
                    padding: '6px 18px',
                    fontWeight: 600,
                    cursor: !selectedDept ? 'not-allowed' : 'pointer',
                    opacity: !selectedDept ? 0.5 : 1,
                    transition: 'all 0.18s',
                    letterSpacing: 0.1,
                  }}
                  onMouseOver={e => e.currentTarget.style.background = '#1565c0'}
                  onMouseOut={e => e.currentTarget.style.background = 'linear-gradient(90deg,#1976d2 60%,#42a5f5 100%)'}
                />
              </div>
            </div>
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
            <ChatPanel
              ref={chatPanelRef}
              collectionName={selectedDept}
              messages={selectedDept ? (chatStates[selectedDept]?.messages || []) : []}
              loading={selectedDept ? (chatStates[selectedDept]?.loading || false) : false}
              setMessages={(updater) => selectedDept && setMessages(selectedDept, updater)}
              setLoading={(value) => selectedDept && setLoading(selectedDept, value)}
              onAnswerToOtherDept={(dept, answerObj) => {
                // 답변 도착한 부서에 답변 추가 및 로딩 해제, 알림 뱃지
                setMessages(dept, prev => [
                  ...prev,
                  {
                    role: 'assistant',
                    content: answerObj.answer,
                    timestamp: answerObj.timestamp,
                  },
                ]);
                setLoading(dept, false);
                setUnreadAnswers(prev => ({ ...prev, [dept]: true }));
              }}
            />
          </div>
        </main>
        {toast && <Toast message={toast} />}
      </div>
    </QueryClientProvider>
  );
}
