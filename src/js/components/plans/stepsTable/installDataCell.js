// @flow

import * as React from 'react';
import Checkbox from '@salesforce/design-system-react/components/checkbox';
import DataTableCell from '@salesforce/design-system-react/components/data-table/cell';
import Icon from '@salesforce/design-system-react/components/icon';
import Spinner from '@salesforce/design-system-react/components/spinner';
import Tooltip from '@salesforce/design-system-react/components/tooltip';

import { CONSTANTS } from 'plans/reducer';

import type { DataCellProps } from 'components/plans/stepsTable/index';

const { STATUS, RESULT_STATUS } = CONSTANTS;

export const InstallDataColumnLabel = (): React.Node => (
  <>
    <span title="Install">Install</span>
    <Tooltip
      align="top right"
      content={
        <span className="step-column-tooltip">Select steps to install.</span>
      }
      triggerClassName="slds-p-left_x-small"
      position="overflowBoundaryElement"
    >
      <a>
        <Icon
          category="utility"
          name="info"
          assistiveText={{
            label: 'Learn More',
          }}
          size="xx-small"
        />
      </a>
    </Tooltip>
  </>
);

const JobCell = (props: DataCellProps): React.Node => {
  const { item, job } = props;
  /* istanbul ignore if */
  if (!item || !job) {
    return null;
  }
  const { id } = item;
  let icon, title;
  if (!job.steps.includes(id)) {
    title = 'skipped';
    icon = (
      <Icon
        category="utility"
        name="dash"
        assistiveText={{
          label: title,
        }}
        size="x-small"
        colorVariant="light"
        className="slds-m-horizontal_x-small"
      />
    );
  } else if (job.completed_steps.includes(id)) {
    title = 'completed';
    icon = (
      <Icon
        category="action"
        name="approval"
        assistiveText={{
          label: title,
        }}
        size="x-small"
        containerClassName="slds-icon-standard-approval"
      />
    );
  } else if (job.status === STATUS.STARTED) {
    let lastCompleted, lastCompletedIdx;
    let activeStep = job.steps[0];
    for (let idx = job.completed_steps.length - 1; idx > -1; idx = idx - 1) {
      lastCompleted = job.completed_steps[idx];
      lastCompletedIdx = job.steps.indexOf(lastCompleted);
      if (lastCompletedIdx > -1) {
        activeStep = job.steps[lastCompletedIdx + 1];
        break;
      }
    }
    if (activeStep && id === activeStep) {
      title = 'installing';
      icon = (
        <>
          <span
            className="slds-is-relative
              slds-m-left_medium
              slds-m-right_large"
          >
            <Spinner size="small" />
          </span>
          Installing...
        </>
      );
    } else {
      title = 'waiting to install';
      icon = (
        <Checkbox
          id={`step-${id}`}
          className="slds-p-around_x-small"
          assistiveText={{
            label: title,
          }}
          checked
          disabled
        />
      );
    }
  } else {
    title = 'not installed';
    icon = (
      <Checkbox
        id={`step-${id}`}
        className="slds-p-around_x-small"
        assistiveText={{
          label: title,
        }}
        checked
        disabled
      />
    );
  }
  return (
    <DataTableCell title={title} {...props}>
      {icon}
    </DataTableCell>
  );
};

class PreflightCell extends React.Component<DataCellProps> {
  handleChange = (
    event: SyntheticInputEvent<HTMLInputElement>,
    { checked }: { checked: boolean },
  ) => {
    const { item, handleStepsChange } = this.props;
    /* istanbul ignore else */
    if (handleStepsChange && item) {
      handleStepsChange(item.id, checked);
    }
  };

  render(): React.Node {
    const { preflight, item, selectedSteps, user } = this.props;
    /* istanbul ignore if */
    if (!item) {
      return null;
    }
    const { id } = item;
    const hasValidToken = user && user.valid_token_for !== null;
    const hasReadyPreflight = preflight && preflight.is_ready;
    const result = preflight && preflight.results && preflight.results[id];
    let skipped, optional;
    if (result) {
      skipped = result.find(res => res.status === RESULT_STATUS.SKIP);
      optional = result.find(res => res.status === RESULT_STATUS.OPTIONAL);
    }
    const required = item.is_required && !optional;
    const recommended = !required && item.is_recommended;
    const disabled =
      Boolean(skipped) || required || !hasValidToken || !hasReadyPreflight;
    let title = 'optional';
    if (skipped) {
      title = skipped.message || 'skipped';
    } else if (required) {
      title = 'required';
    } else if (recommended) {
      title = 'recommended';
    }
    let label = '';
    if (skipped && skipped.message) {
      label = skipped.message;
    } else if (recommended) {
      label = 'recommended';
    }
    return (
      <DataTableCell title={title} {...this.props}>
        <Checkbox
          id={`step-${id}`}
          checked={selectedSteps && selectedSteps.has(id)}
          disabled={disabled}
          className="slds-p-vertical_x-small"
          labels={{ label }}
          assistiveText={{
            label: title,
          }}
          onChange={this.handleChange}
        />
      </DataTableCell>
    );
  }
}

const InstallDataCell = (props: DataCellProps): React.Node => {
  if (props.job) {
    return <JobCell {...props} />;
  }
  return <PreflightCell {...props} />;
};
InstallDataCell.displayName = DataTableCell.displayName;

export default InstallDataCell;
