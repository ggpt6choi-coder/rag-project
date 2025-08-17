import React, { useRef, useState } from 'react';
import DocumentsModal from './DocumentsModal.mui';
import { useMutation } from 'react-query';

async function uploadFile({ file, collectionName }) {
  const formData = new FormData();
  formData.append('file', file);
  if (collectionName) formData.append('collection_name', collectionName);
  const res = await fetch('/api/v1/upload-file', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('업로드 실패');
  return res.json();
}

export default function FileUpload({ collectionName, onSuccess, disabled, small }) {
  const inputRef = useRef();
  const [uploading, setUploading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const mutation = useMutation(uploadFile, {
    onSuccess: (data) => {
      if (data && data.document_id) {
        setUploading(false);
        setDone(true);
        onSuccess && onSuccess('파일 업로드가 완료되었습니다');
        setTimeout(() => setDone(false), 1500);
      } else {
        setUploading(false);
        setError('업로드 응답 오류');
      }
    },
    onError: () => {
      alert('업로드 실패');
      setUploading(false);
      setError('업로드 실패');
    },
  });

  // 진행상태 폴링 제거: 업로드 성공만 체크

  // 진행률 폴링 및 바 제거: 단순 완료 알림만 표시

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setDone(false);
    setError(null);
    mutation.mutate({ file, collectionName });
  };

  return (
    <div style={{ position: 'relative', display: 'flex', alignItems: 'center', height: small ? 32 : 44, flexDirection: 'row', width: '100%' }}>
      <label
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: small ? 7 : 12,
          background: uploading || disabled ? '#bdbdbd' : 'linear-gradient(90deg,#1976d2 60%,#42a5f5 100%)',
          color: '#fff',
          borderRadius: 18,
          padding: small ? '6px 16px 6px 12px' : '12px 34px 12px 20px',
          fontWeight: 600,
          fontSize: small ? 14 : 16,
          boxShadow: small ? '0 2px 6px rgba(25, 118, 210, 0.10)' : '0 4px 16px rgba(25, 118, 210, 0.13)',
          cursor: uploading || disabled ? 'not-allowed' : 'pointer',
          opacity: uploading || disabled ? 0.6 : 1,
          transition: 'all 0.18s',
          border: 'none',
          outline: 'none',
          position: 'relative',
          minWidth: small ? 80 : 120,
          letterSpacing: 0.1,
        }}
        htmlFor="file-upload-input"
      >
        <span style={{ fontSize: small ? 15 : 18, marginRight: 4 }}>📎</span>
        {uploading ? (
          <>
            <span>업로드 중...</span>
            <span className="spinner" style={{ marginLeft: 8, width: 16, height: 16, border: '2px solid #fff', borderTop: '2px solid #1976d2', borderRadius: '50%', display: 'inline-block', animation: 'spin 1s linear infinite', verticalAlign: 'middle' }} />
          </>
        ) : done ? '업로드 완료' : '파일 업로드'}
        <input
          id="file-upload-input"
          ref={inputRef}
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          disabled={uploading || disabled}
        />
      </label>
      <button
        style={{
          marginLeft: 16,
          padding: small ? '6px 16px' : '12px 24px',
          borderRadius: 18,
          background: !collectionName || uploading || disabled ? '#f5f5f5' : '#fff',
          color: !collectionName || uploading || disabled ? '#bdbdbd' : '#1976d2',
          fontWeight: 600,
          fontSize: small ? 14 : 16,
          border: '1.5px solid #1976d2',
          cursor: !collectionName || uploading || disabled ? 'not-allowed' : 'pointer',
          opacity: !collectionName || uploading || disabled ? 0.6 : 1,
          boxShadow: '0 2px 8px rgba(25, 118, 210, 0.07)',
          transition: 'all 0.18s',
        }}
        onClick={() => { if (collectionName && !uploading && !disabled) setModalOpen(true); }}
        disabled={!collectionName || uploading || disabled}
      >
        업로드 파일 목록
      </button>
      {error && (
        <div style={{ width: '100%', marginTop: 6, fontSize: 13, color: '#d32f2f', minHeight: 18 }}>{error}</div>
      )}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      <DocumentsModal open={modalOpen} onClose={() => setModalOpen(false)} collectionName={collectionName} />
    </div>
  );
}
