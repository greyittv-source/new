import { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('daily');
  
  // 상태 관리 (localStorage 연동)
  const [dailyTasks, setDailyTasks] = useState(() => {
    const saved = localStorage.getItem('greyit_daily');
    return saved ? JSON.parse(saved) : Array(9).fill({ insta: false, tiktok: false });
  });

  const [milestones, setMilestones] = useState(() => {
    const saved = localStorage.getItem('greyit_milestones');
    return saved ? JSON.parse(saved) : [
      { id: 1, text: '유튜브 구독자 100명 달성', completed: false },
      { id: 2, text: '틱톡 첫 1k 조회수 달성', completed: false },
      { id: 3, text: '인스타 릴스 5일 연속 업로드', completed: false },
      { id: 4, text: '레딧 Lofi 커뮤니티 첫 게시물 작성', completed: false },
    ];
  });

  // 챗(호출기) 상태
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  // 메시지 자동 스크롤
  useEffect(() => {
    if (activeTab === 'pager' && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, activeTab]);

  // 주기적으로 Luna의 답변 폴링 (5초마다)
  useEffect(() => {
    let interval;
    if (activeTab === 'pager') {
      interval = setInterval(async () => {
        try {
          const res = await fetch('https://dweet.io/get/latest/dweet/for/greyit-luna-to-ceo-7x9q2w1z');
          const data = await res.json();
          if (data.with && data.with.length > 0) {
            const content = data.with[0].content;
            if (content && content.text && content.msgId) {
              setMessages(prev => {
                // 이미 있는 메시지인지 확인
                if (!prev.find(m => m.msgId === content.msgId)) {
                  return [...prev, { sender: 'luna', text: content.text, msgId: content.msgId }];
                }
                return prev;
              });
            }
          }
        } catch (e) {
          console.error("Failed to fetch Luna's messages", e);
        }
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [activeTab]);

  const sendMessage = async () => {
    if (!inputText.trim()) return;
    const newMsg = { sender: 'ceo', text: inputText, msgId: Date.now().toString() };
    setMessages(prev => [...prev, newMsg]);
    setInputText('');

    try {
      await fetch('https://dweet.io/dweet/for/greyit-ceo-to-luna-7x9q2w1z', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newMsg)
      });
    } catch (e) {
      console.error("Failed to send message", e);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  useEffect(() => {
    localStorage.setItem('greyit_daily', JSON.stringify(dailyTasks));
  }, [dailyTasks]);

  useEffect(() => {
    localStorage.setItem('greyit_milestones', JSON.stringify(milestones));
  }, [milestones]);

  const toggleDaily = (dayIndex, platform) => {
    const newTasks = [...dailyTasks];
    newTasks[dayIndex] = { ...newTasks[dayIndex], [platform]: !newTasks[dayIndex][platform] };
    setDailyTasks(newTasks);
  };

  const toggleMilestone = (id) => {
    setMilestones(milestones.map(m => m.id === id ? { ...m, completed: !m.completed } : m));
  };

  return (
    <div className="dashboard-container">
      <aside className="sidebar glass-panel">
        <div className="logo-area">
          <h1>Greyit TV Studio</h1>
          <p>Global AI Music Enterprise</p>
        </div>
        
        <button 
          className={`nav-btn ${activeTab === 'daily' ? 'active' : ''}`}
          onClick={() => setActiveTab('daily')}
        >
          📅 일간 업로드 체크리스트
        </button>
        <button 
          className={`nav-btn ${activeTab === 'milestone' ? 'active' : ''}`}
          onClick={() => setActiveTab('milestone')}
        >
          🚀 채널 로드맵 & 목표
        </button>
        <button 
          className={`nav-btn ${activeTab === 'pager' ? 'active' : ''}`}
          onClick={() => setActiveTab('pager')}
        >
          📡 핫라인 (루나 호출기)
        </button>
      </aside>

      <main className="main-content glass-panel">
        {activeTab === 'daily' && (
          <>
            <div className="header">
              <h2>📅 일간 업로드 현황 (Day 1 ~ Day 9)</h2>
            </div>
            <div className="task-list">
              {dailyTasks.map((task, idx) => (
                <div key={idx} className="task-card">
                  <h3>Day {idx + 1} 업로드 퀘스트</h3>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input 
                        type="checkbox" 
                        checked={task.insta} 
                        onChange={() => toggleDaily(idx, 'insta')} 
                      />
                      <span>Instagram (릴스)</span>
                    </label>
                    <label className="checkbox-label">
                      <input 
                        type="checkbox" 
                        checked={task.tiktok} 
                        onChange={() => toggleDaily(idx, 'tiktok')} 
                      />
                      <span>TikTok (쇼츠)</span>
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {activeTab === 'milestone' && (
          <>
            <div className="header">
              <h2>🚀 채널 마일스톤 (Milestones)</h2>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                목표를 달성할 때마다 체크하세요. 작은 성취가 모여 위대한 결과를 만듭니다. (Greyit = Great)
              </p>
              {milestones.map(m => (
                <div key={m.id} className={`milestone-item ${m.completed ? 'completed' : ''}`}>
                  <input 
                    type="checkbox" 
                    checked={m.completed} 
                    onChange={() => toggleMilestone(m.id)} 
                  />
                  <span style={{ textDecoration: m.completed ? 'line-through' : 'none' }}>
                    {m.text}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}

        {activeTab === 'pager' && (
          <div className="pager-container">
            <div className="header">
              <h2>📡 루나 호출기 (Hotline to Luna)</h2>
            </div>
            <p className="pager-desc">이동 중에도 PC 시스템에 상주하는 총괄 매니저 루나를 깨워 메시지를 남길 수 있습니다.</p>
            
            <div className="chat-box">
              {messages.length === 0 && (
                <div className="empty-chat">아직 주고받은 메시지가 없습니다. 루나에게 인사를 건네보세요!</div>
              )}
              {messages.map((msg, idx) => (
                <div key={idx} className={`chat-bubble ${msg.sender}`}>
                  <div className="chat-sender">{msg.sender === 'ceo' ? '😎 대표님' : '🤖 루나 (Luna)'}</div>
                  <div className="chat-text">{msg.text}</div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
              <input 
                type="text" 
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="루나에게 메시지 보내기..." 
                className="chat-input"
              />
              <button onClick={sendMessage} className="chat-send-btn">전송</button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
