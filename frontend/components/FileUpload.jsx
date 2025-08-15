import React, { useRef, useState } from 'react';
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
  const mutation = useMutation(uploadFile, {
    onSuccess: (data) => {
      onSuccess && onSuccess('새로운 데이터가 추가되었습니다');
      setUploading(false);
    },
    onError: () => {
      alert('업로드 실패');
      setUploading(false);
    },
  });

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    mutation.mutate({ file, collectionName });
  };

  return (
    <div style={{ position: 'relative', display: 'flex', alignItems: 'center', height: small ? 32 : 44 }}>
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
        {uploading ? '업로드 중...' : '파일 업로드'}
        <input
          id="file-upload-input"
          ref={inputRef}
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          disabled={uploading || disabled}
        />
      </label>
    </div>
  );
}
