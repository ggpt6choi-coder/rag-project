import React, { useEffect, useState } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';

export default function DocumentsModal({ open, onClose, collectionName }) {
    const [docs, setDocs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!open) return;
        setLoading(true);
        const url = collectionName ? `/api/v1/documents?collection_name=${encodeURIComponent(collectionName)}` : '/api/v1/documents';
        fetch(url)
            .then(res => res.json())
            .then(data => {
                setDocs(data.documents || []);
                setLoading(false);
            })
            .catch(() => {
                setError('목록을 불러오지 못했습니다');
                setLoading(false);
            });
    }, [open, collectionName]);

    const handleDownload = (doc) => {
        const url = `/api/v1/download/${encodeURIComponent(doc.document_id)}`;
        const link = document.createElement('a');
        link.href = url;
        // 파일명 지정 (백엔드에서 Content-Disposition 헤더가 있으면 자동 적용됨)
        link.setAttribute('download', '');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
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

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle sx={{ m: 0, p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                업로드 파일 목록
                <IconButton aria-label="close" onClick={onClose} sx={{ color: (theme) => theme.palette.grey[500] }}>
                    <CloseIcon />
                </IconButton>
            </DialogTitle>
            <DialogContent dividers>
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
                                    <td style={{ padding: 8 }}><Button variant="outlined" size="small" onClick={() => handleDownload(doc)}>다운로드</Button></td>
                                    <td style={{ padding: 8 }}><Button variant="outlined" size="small" color="error" onClick={() => handleDelete(doc)}>삭제</Button></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">닫기</Button>
            </DialogActions>
        </Dialog>
    );
}
