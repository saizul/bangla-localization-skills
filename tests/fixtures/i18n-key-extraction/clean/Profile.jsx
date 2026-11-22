import { FormattedMessage, useIntl } from "react-intl";

export default function Profile({ user }) {
  const intl = useIntl();
  return (
    <section className="profile-card">
      <h1><FormattedMessage id="profile.title" defaultMessage="Your profile" /></h1>
      <img src={user.avatar} alt={intl.formatMessage({ id: "profile.avatar_alt" })} />
      <p>{intl.formatMessage({ id: "profile.greeting" }, { name: user.name })}</p>
    </section>
  );
}
