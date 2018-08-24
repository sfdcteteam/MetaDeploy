// @flow

import * as React from 'react';
import DocumentTitle from 'react-document-title';
import { Link } from 'react-router-dom';

const FourOhFour = () => (
  <DocumentTitle title="404 | MetaDeploy">
    <div>
      <h1 className="slds-text-heading_large">Oh Noes!</h1>
      <p>
        That page cannot be found. Try the <Link to="/">home page</Link>?
      </p>
    </div>
  </DocumentTitle>
);

export default FourOhFour;
