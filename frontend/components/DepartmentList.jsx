import React from 'react';

const DEPARTMENTS = [
  '경영지원팀',
  '인사팀',
  '재무팀',
  '영업팀',
  '마케팅팀',
  'IT팀',
  '연구개발팀',
  '고객지원팀',
  '생산팀',
  '품질관리팀',
];

export default function DepartmentList({ selected, onSelect, unreadAnswers = {} }) {
  return (
    <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '28px 0 0 0', background: '#202123', color: '#fff', minHeight: 0 }}>
      <ul style={{ flex: 1, overflowY: 'auto', padding: 0, margin: 0, listStyle: 'none', scrollbarWidth: 'thin', scrollbarColor: '#353740 #202123' }}>
        {DEPARTMENTS.map((dept) => (
          <li
            key={dept}
            style={{
              cursor: 'pointer',
              padding: '15px 36px',
              borderRadius: 12,
              margin: '0 14px 8px 14px',
              background: selected === dept ? 'linear-gradient(90deg,#1976d2 60%,#353740 100%)' : 'transparent',
              color: selected === dept ? '#fff' : '#bdbdbd',
              fontWeight: selected === dept ? 700 : 400,
              border: selected === dept ? '1.5px solid #1976d2' : '1px solid transparent',
              transition: 'all 0.18s',
              boxShadow: selected === dept ? '0 4px 16px rgba(25, 118, 210, 0.13)' : 'none',
              display: 'flex',
              alignItems: 'center',
              fontSize: 17,
              letterSpacing: 0.2,
            }}
            onClick={() => onSelect(dept)}
            onMouseOver={e => e.currentTarget.style.background = selected === dept ? 'linear-gradient(90deg,#1976d2 60%,#353740 100%)' : '#26272b'}
            onMouseOut={e => e.currentTarget.style.background = selected === dept ? 'linear-gradient(90deg,#1976d2 60%,#353740 100%)' : 'transparent'}
          >
            <span style={{ marginRight: 14, fontSize: 20, opacity: 0.8 }}>🏢</span>
            {dept}
            {unreadAnswers[dept] && (
              <span style={{
                marginLeft: 10,
                background: '#ff1744',
                color: '#fff',
                borderRadius: '50%',
                width: 14,
                height: 14,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 11,
                fontWeight: 700,
                boxShadow: '0 1px 4px rgba(0,0,0,0.13)',
                verticalAlign: 'middle',
              }}>●</span>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}
