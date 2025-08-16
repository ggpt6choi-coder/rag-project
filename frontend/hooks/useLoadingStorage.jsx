import { useState, useEffect } from 'react';

// 부서별로 로딩 상태를 로컬스토리지에 저장/불러오기
export default function useLoadingStorage(collectionName) {
    const key = collectionName ? `chat_loading_${collectionName}` : null;
    const [loading, setLoading] = useState(false);

    // 부서 변경 시 로딩 상태 불러오기
    useEffect(() => {
        if (!key) {
            setLoading(false);
            return;
        }
        try {
            const saved = localStorage.getItem(key);
            setLoading(saved === 'true');
        } catch {
            setLoading(false);
        }
    }, [key]);

    // loading이 바뀔 때마다 저장
    useEffect(() => {
        if (!key) return;
        localStorage.setItem(key, loading ? 'true' : 'false');
    }, [key, loading]);

    return [loading, setLoading];
}
