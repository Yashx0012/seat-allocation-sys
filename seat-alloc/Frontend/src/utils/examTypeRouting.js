const CREATE_PLAN_STICKY_MODE_KEY = 'createPlanStickyMode';

const MINOR_FLOW_EXACT_PATHS = new Set([
  '/create-plan',
  '/minor-exam/create-plan',
  '/upload',
  '/allocation',
  '/template-editor',
  '/classroom',
  '/manual-allocation'
]);

const MINOR_FLOW_PREFIXES = [
  '/attendance/',
  '/more-options/'
];

export const setMinorCreatePlanStickyMode = () => {
  sessionStorage.setItem(CREATE_PLAN_STICKY_MODE_KEY, 'minor');
};

export const getCreatePlanStickyMode = () => {
  return sessionStorage.getItem(CREATE_PLAN_STICKY_MODE_KEY);
};

export const clearCreatePlanStickyMode = () => {
  sessionStorage.removeItem(CREATE_PLAN_STICKY_MODE_KEY);
};

export const isMinorCreatePlanFlowPath = (pathname = '') => {
  return (
    MINOR_FLOW_EXACT_PATHS.has(pathname) ||
    MINOR_FLOW_PREFIXES.some((prefix) => pathname.startsWith(prefix))
  );
};
