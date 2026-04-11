import { Star } from 'lucide-react';

const StarRating = ({ rating, maxRating = 5, onRatingChange, size = 5, interactive = false }) => {
  const stars = [];

  for (let i = 1; i <= maxRating; i++) {
    stars.push(
      <Star
        key={i}
        className={`w-${size} h-${size} ${
          i <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        } ${interactive ? 'cursor-pointer hover:text-yellow-400 transition-colors' : ''}`}
        onClick={() => interactive && onRatingChange && onRatingChange(i)}
      />
    );
  }

  return <div className="flex space-x-1">{stars}</div>;
};

export default StarRating;
