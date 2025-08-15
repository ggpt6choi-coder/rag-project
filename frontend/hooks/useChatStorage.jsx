import { useState, useEffect } from 'react';

// 부서별로 로컬스토리지에 채팅 기록 저장/불러오기
export default function useChatStorage(collectionName) {
  const key = collectionName ? `chat_history_${collectionName}` : null;
  const [messages, setMessages] = useState([]);

  // 부서 변경 시 기록 불러오기 (key가 바뀔 때마다 항상 동기화)
  useEffect(() => {
    if (!key) {
      setMessages([]);
      return;
    }
    try {
      const saved = localStorage.getItem(key);
      setMessages(saved ? JSON.parse(saved) : []);
    } catch {
      setMessages([]);
    }
  }, [key]);

  // messages가 바뀔 때마다 저장
  useEffect(() => {
    if (!key) return;
    localStorage.setItem(key, JSON.stringify(messages));
  }, [key, messages]);

  return [messages, setMessages];
}
