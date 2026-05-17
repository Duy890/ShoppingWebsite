import { Link } from 'react-router-dom';

const AuthFooter = ({ message, linkText, linkTo }) => {
  return (
    <p className="mt-8 text-center text-sm leading-6 text-slate-500 dark:text-slate-400">
      {message}{' '}
      <Link to={linkTo} className="font-semibold text-primary hover:text-orange-600 transition-colors">
        {linkText}
      </Link>
    </p>
  );
};

export default AuthFooter;
