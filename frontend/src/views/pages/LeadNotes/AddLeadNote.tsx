import React, { useState, useEffect, useRef } from 'react';
import { leadNoteApi } from './api/apiLeadNotes';

interface NoteItem {
    id: number;
    note: string;
    added_by: string | number;
    added_by_name?: string;
    timestamp: string;
}

interface AddLeadNoteProps {
    leadId: number;
    onNoteAdded?: () => void;
}

function formatNoteDate(dateStr: string) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const day = date.getDate().toString().padStart(2, '0');
    const month = date.toLocaleString('en-US', { month: 'short' });
    const year = date.getFullYear().toString().slice(-2);
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${day}-${month}-${year} ${hours}:${minutes} ${ampm}`;
}

const AddLeadNote: React.FC<AddLeadNoteProps> = ({ leadId, onNoteAdded }) => {
    const [note, setNote] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [notes, setNotes] = useState<NoteItem[]>([]);
    const [fetchingNotes, setFetchingNotes] = useState(false);
    const [listening, setListening] = useState(false);
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        // Only set up SpeechRecognition if available
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                setNote(prev => prev + (prev ? ' ' : '') + transcript);
            };
            recognitionRef.current.onend = () => setListening(false);
        }
    }, []);

    const handleMicClick = () => {
        if (!recognitionRef.current) return;
        if (listening) {
            recognitionRef.current.stop();
            setListening(false);
        } else {
            recognitionRef.current.start();
            setListening(true);
        }
    };

    useEffect(() => {
        fetchNotes();
        // eslint-disable-next-line
    }, [leadId]);

    const fetchNotes = async () => {
        setFetchingNotes(true);
        try {
            const res = await leadNoteApi.getNotesByLead(leadId);
            let notesArray: any[] = [];
            if (Array.isArray(res)) {
                notesArray = res;
            } else if (res && Array.isArray((res as any).results)) {
                notesArray = (res as any).results;
            }
            setNotes(
                notesArray.map((n: any) => ({
                    id: n.id,
                    note: n.note || n.lead_note,
                    added_by: n.added_by_name || n.added_by || 'Unknown',
                    added_by_name: n.added_by_name,
                    timestamp: n.created_at || n.timestamp || '',
                }))
            );
        } catch {
            setNotes([]);
        } finally {
            setFetchingNotes(false);
        }
    };

    const handleAddNote = async () => {
        if (!note.trim()) {
            setError('Note cannot be empty.');
            return;
        }
        setLoading(true);
        setError(null);
        setSuccess(false);
        try {
            await leadNoteApi.createNote({ lead: leadId, lead_note: note });
            setNote('');
            setSuccess(true);
            fetchNotes();
            if (onNoteAdded) onNoteAdded();
        } catch (err: any) {
            setError(err?.message || 'Failed to add note.');
        } finally {
            setLoading(false);
        }
    };

    const SpeechSupported = typeof window !== 'undefined' && ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);

    return (
        <div style={{ width: 420, minHeight: 400, maxHeight: 600, display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: 16, flexShrink: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginBottom: 8 }}>
                    {SpeechSupported && (
                        <button
                            type="button"
                            onClick={handleMicClick}
                            style={{
                                background: listening ? '#be2073' : '#eee',
                                color: listening ? 'white' : '#333',
                                border: 'none',
                                borderRadius: '50%',
                                width: 36,
                                height: 36,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                            }}
                            title={listening ? 'Stop Listening' : 'Start Speech to Text'}
                        >
                            🎤
                        </button>
                    )}
                </div>
                <textarea
                    value={note}
                    onChange={e => setNote(e.target.value)}
                    placeholder="Write your note here..."
                    rows={5}
                    style={{
                        width: '100%',
                        minHeight: 80,
                        border: '1px solid #d1d5db',
                        borderRadius: 6,
                        padding: 10,
                        outline: 'none',
                        fontSize: 16,
                        boxSizing: 'border-box',
                        transition: 'border-color 0.2s',
                    }}
                    onFocus={e => (e.currentTarget.style.borderColor = '#be2073')}
                    onBlur={e => (e.currentTarget.style.borderColor = '#d1d5db')}
                    disabled={loading}
                />
                <button
                    onClick={handleAddNote}
                    disabled={loading}
                    style={{
                        marginTop: 10,
                        background: '#be2073',
                        color: 'white',
                        border: 'none',
                        borderRadius: 4,
                        padding: '8px 20px',
                        fontWeight: 600,
                        fontSize: 16,
                        cursor: loading ? 'not-allowed' : 'pointer',
                        boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                        transition: 'background 0.2s',
                    }}
                >
                    {loading ? 'Adding...' : 'Add Note'}
                </button>
                {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
                {success && <div style={{ color: 'green', marginTop: 8 }}>Note added successfully!</div>}
            </div>
            <div style={{ flex: 1, minHeight: 180, maxHeight: 250, overflowY: 'auto', border: '1px solid #e5e7eb', borderRadius: 6, padding: 10, background: '#fafbfc' }}>
                <div style={{ fontWeight: 600, marginBottom: 8 }}>Notes</div>
                {fetchingNotes ? (
                    <div>Loading notes...</div>
                ) : notes.length === 0 ? (
                    <div style={{ color: '#888' }}>No notes yet.</div>
                ) : (
                    notes.map(n => (
                        <div key={n.id} style={{ marginBottom: 14, paddingBottom: 8, borderBottom: '1px solid #eee', position: 'relative', minHeight: 40, display: 'flex', flexDirection: 'column' }}>
                            <div style={{ fontSize: 15, marginBottom: 2, wordBreak: 'break-word' }}>{n.note}</div>
                            <div style={{
                                fontSize: 12,
                                color: '#666',
                                alignSelf: 'flex-end',
                                marginTop: 4
                            }}>
                                {n.added_by_name || n.added_by}
                                {n.timestamp && (
                                    <span>{', '}{formatNoteDate(n.timestamp)}</span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default AddLeadNote;
