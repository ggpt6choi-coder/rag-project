import React, { useEffect, useState } from 'react';

export default function DocumentsModal({ open, onClose }) {
    const [docs, setDocs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!open) return;
        setLoading(true);
        fetch('/api/v1/documents')
            .then(res => res.json())
            .then(data => {
                setDocs(data.documents || []);
                setLoading(false);
            })
            .catch(() => {
                setError('목록을 불러오지 못했습니다');
                setLoading(false);
            });
    }, [open]);

    const handleDownload = (doc) => {
        window.open(`/api/v1/download/${encodeURIComponent(doc.document_id)}`);
    };

    const handleDelete = (doc) => {
        if (!window.confirm('정말 삭제하시겠습니까?')) return;
        fetch(`/api/v1/documents/${encodeURIComponent(doc.document_id)}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(() => {
                setDocs(docs.filter(d => d.document_id !== doc.document_id));
            })
            .catch(() => alert('삭제 실패'));
    };

    if (!open) return null;
    return (
        <div style={{ position: 'fixed', left: 0, top: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: '#fff', borderRadius: 12, minWidth: 400, maxWidth: 600, padding: 24, boxShadow: '0 4px 24px rgba(0,0,0,0.13)' }}>
                <h2 style={{ marginTop: 0 }}>업로드 파일 목록</h2>
                <button onClick={onClose} style={{ position: 'absolute', right: 32, top: 24, fontSize: 18, background: 'none', border: 'none', cursor: 'pointer' }}>✕</button>
                {loading ? <div>불러오는 중...</div> : error ? <div style={{ color: 'red' }}>{error}</div> : (
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
                        <thead>
                            <tr style={{ background: '#f5f5f5' }}>
                                <th style={{ padding: 8, borderBottom: '1px solid #eee' }}>파일명</th>
                                <th style={{ padding: 8, borderBottom: '1px solid #eee' }}>다운로드</th>
                                <th style={{ padding: 8, borderBottom: '1px solid #eee' }}>삭제</th>
                            </tr>
                        </thead>
                        <tbody>
                            {docs.length === 0 ? (
                                <tr><td colSpan={3} style={{ textAlign: 'center', padding: 16 }}>업로드된 파일이 없습니다</td></tr>
                            ) : docs.map(doc => (
                                <tr key={doc.document_id}>
                                    <td style={{ padding: 8 }}>{doc.metadata?.filename || doc.document_id}</td>
                                    <td style={{ padding: 8 }}><button onClick={() => handleDownload(doc)}>다운로드</button></td>
                                    <td style={{ padding: 8 }}><button onClick={() => handleDelete(doc)} style={{ color: 'red' }}>삭제</button></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
