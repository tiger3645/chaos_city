import { useState, useCallback, useEffect } from 'react';
import {
    CardPlayedMessage,
    EffectContinuedMessage,
    RevealedInfo,
    EffectChoice,
    CardStatsMessage,
    AttackResultMessage,
    EffectsTriggeredMessage,
    CardStats
} from '../types/effects';
import { WebSocketMessage } from '../types/game';
import { EffectNotification } from '../components/EffectNotification';

export const useEffects = (
    lastMessage: WebSocketMessage | null,
    continueEffect: (playerId: string, effectId: string, chosenValue: any) => void,
    getCardStats: (cardGameId: string) => void
) => {
    // Effect modal state
    const [effectModalOpen, setEffectModalOpen] = useState(false);
    const [effectMessage, setEffectMessage] = useState('');
    const [effectChoices, setEffectChoices] = useState<EffectChoice[]>([]);
    const [currentEffectId, setCurrentEffectId] = useState<string | null>(null);
    const [currentPlayerId, setCurrentPlayerId] = useState<string | null>(null);

    // Revealed info modal state
    const [revealedInfoModalOpen, setRevealedInfoModalOpen] = useState(false);
    const [revealedInfo, setRevealedInfo] = useState<RevealedInfo | null>(null);

    // Card stats cache
    const [cardStatsCache, setCardStatsCache] = useState<Record<string, CardStats>>({});

    // Notifications
    const [notifications, setNotifications] = useState<EffectNotification[]>([]);

    // Add notification
    const addNotification = useCallback((message: string, type: 'effect' | 'trigger' | 'info' = 'effect') => {
        const notification: EffectNotification = {
            id: `${Date.now()}-${Math.random()}`,
            message,
            type,
            duration: 3000
        };
        setNotifications(prev => [...prev, notification]);
    }, []);

    // Dismiss notification
    const dismissNotification = useCallback((id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    }, []);

    // Handle effect choice
    const handleEffectChoice = useCallback((choice: EffectChoice) => {
        if (currentEffectId && currentPlayerId) {
            continueEffect(currentPlayerId, currentEffectId, choice.id);
            setEffectModalOpen(false);
        }
    }, [currentEffectId, currentPlayerId, continueEffect]);

    // Cancel effect modal
    const handleCancelEffect = useCallback(() => {
        setEffectModalOpen(false);
        setCurrentEffectId(null);
        setCurrentPlayerId(null);
    }, []);

    // Close revealed info modal
    const closeRevealedInfoModal = useCallback(() => {
        setRevealedInfoModalOpen(false);
        setRevealedInfo(null);
    }, []);

    // Request card stats
    const requestCardStats = useCallback((cardGameId: string) => {
        if (!cardStatsCache[cardGameId]) {
            getCardStats(cardGameId);
        }
    }, [cardStatsCache, getCardStats]);

    // Get cached card stats
    const getCachedCardStats = useCallback((cardGameId: string): CardStats | undefined => {
        return cardStatsCache[cardGameId];
    }, [cardStatsCache]);

    // Process messages
    useEffect(() => {
        if (!lastMessage) return;

        switch (lastMessage.type) {
            case 'card_played': {
                const msg = lastMessage as CardPlayedMessage;

                if (msg.requires_choice) {
                    // Show effect modal
                    setEffectMessage(msg.message);
                    setEffectChoices(msg.choices);
                    setCurrentEffectId(msg.effect_id || null);
                    setCurrentPlayerId(msg.player_id);
                    setEffectModalOpen(true);
                } else if (msg.revealed_info) {
                    // Show revealed info modal
                    setRevealedInfo(msg.revealed_info);
                    setRevealedInfoModalOpen(true);
                } else {
                    // Show notification
                    addNotification(msg.message, 'effect');
                }
                break;
            }

            case 'effect_continued': {
                const msg = lastMessage as EffectContinuedMessage;

                if (msg.requires_choice) {
                    // Show effect modal for next step
                    setEffectMessage(msg.message);
                    setEffectChoices(msg.choices);
                    setCurrentEffectId(msg.effect_id || null);
                    // Keep current player ID
                    setEffectModalOpen(true);
                } else if (msg.revealed_info) {
                    // Show revealed info modal
                    setRevealedInfo(msg.revealed_info);
                    setRevealedInfoModalOpen(true);
                } else {
                    // Effect completed
                    addNotification(msg.message, 'effect');
                    setEffectModalOpen(false);
                    setCurrentEffectId(null);
                }
                break;
            }

            case 'card_stats': {
                const msg = lastMessage as CardStatsMessage;
                setCardStatsCache(prev => ({
                    ...prev,
                    [msg.card_game_id]: msg.stats
                }));
                break;
            }

            case 'attack_result': {
                const msg = lastMessage as AttackResultMessage;
                if (msg.result.triggered_effects && msg.result.triggered_effects.length > 0) {
                    msg.result.triggered_effects.forEach(effect => {
                        addNotification(effect, 'trigger');
                    });
                }
                break;
            }

            case 'effects_triggered': {
                const msg = lastMessage as EffectsTriggeredMessage;
                if (msg.effects && msg.effects.length > 0) {
                    msg.effects.forEach(effect => {
                        addNotification(effect, 'trigger');
                    });
                }
                break;
            }
        }
    }, [lastMessage, addNotification]);

    return {
        // Effect modal
        effectModalOpen,
        effectMessage,
        effectChoices,
        handleEffectChoice,
        handleCancelEffect,

        // Revealed info modal
        revealedInfoModalOpen,
        revealedInfo,
        closeRevealedInfoModal,

        // Card stats
        requestCardStats,
        getCachedCardStats,
        cardStatsCache,

        // Notifications
        notifications,
        dismissNotification
    };
};

export default useEffects;
