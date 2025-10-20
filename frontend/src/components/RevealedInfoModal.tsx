import React from 'react';
import { X, Eye } from 'lucide-react';
import { RevealedInfo } from '../types/effects';
import Card from './Card';
import { Card as CardType } from '../types/game';

interface RevealedInfoModalProps {
    isOpen: boolean;
    revealedInfo: RevealedInfo | null;
    onClose: () => void;
}

const RevealedInfoModal: React.FC<RevealedInfoModalProps> = ({
    isOpen,
    revealedInfo,
    onClose
}) => {
    if (!isOpen || !revealedInfo) return null;

    const getTitle = () => {
        switch (revealedInfo.type) {
            case 'hand':
                return "Opponent's Hand Revealed";
            case 'deck':
                return 'Deck Cards Revealed';
            case 'field':
                return 'Field Cards Revealed';
            default:
                return 'Information Revealed';
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 animate-fade-in">
            <div className="bg-gray-900 rounded-lg p-6 max-w-6xl w-full mx-4 border-2 border-blue-500 shadow-2xl animate-scale-in max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <Eye className="w-7 h-7 text-blue-400" />
                        <h2 className="text-3xl font-bold text-white">{getTitle()}</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Message */}
                {revealedInfo.message && (
                    <div className="mb-6 p-4 bg-blue-900 bg-opacity-30 rounded border border-blue-400">
                        <p className="text-lg text-white">{revealedInfo.message}</p>
                    </div>
                )}

                {/* Cards Grid */}
                {revealedInfo.cards && revealedInfo.cards.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {revealedInfo.cards.map((card, index) => (
                            <div key={card.id || index} className="flex justify-center">
                                <Card card={card as CardType} />
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8 text-gray-400">
                        <p>No cards to display</p>
                    </div>
                )}

                {/* Close Button */}
                <div className="mt-6 flex justify-center">
                    <button
                        onClick={onClose}
                        className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold 
                                 rounded-lg transition-colors transform hover:scale-105"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RevealedInfoModal;
