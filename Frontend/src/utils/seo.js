export const generateBreadcrumbSchema = (breadcrumbs = [], baseUrl = '') => {
  if (!breadcrumbs || breadcrumbs.length === 0 || !baseUrl) {
    return null;
  }
  
  const items = breadcrumbs.map((crumb, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    name: crumb.name,
    ...(crumb.url && { item: `${baseUrl}${crumb.url}` })
  }));
  
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items
  };
};

export const injectBreadcrumbSchema = (breadcrumbs = [], baseUrl = '') => {
  const schema = generateBreadcrumbSchema(breadcrumbs, baseUrl);
  if (!schema) return '';
  
  return JSON.stringify(schema);
};

export const createBreadcrumbMeta = (breadcrumbs = []) => {
  if (!breadcrumbs || breadcrumbs.length === 0) {
    return [];
  }
  
  return breadcrumbs.map((crumb, index) => ({
    rel: index === 0 ? 'index' : 'subsection',
    ...(crumb.url && { href: crumb.url }),
    title: crumb.name
  }));
};